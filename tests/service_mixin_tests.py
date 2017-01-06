import json
import socket

from rejected import consumer
from tornado import concurrent, gen, httpclient, testing
import helper.config
import mock

from vetoes import service


class Consumer(service.HTTPServiceMixin):

    def __init__(self, *args, **kwargs):
        kwargs['service_map'] = {'fetch-stats': 'httpbin'}
        super(Consumer, self).__init__(*args, **kwargs)

    @gen.coroutine
    def process(self):
        yield self.call_http_service('fetch-stats', 'GET', 'stats')

    def get_service_url(self, service, *path, **kwargs):
        return 'http://httpbin.org/status/200'


class HTTPServiceMixinTests(testing.AsyncTestCase):

    def setUp(self):
        super(HTTPServiceMixinTests, self).setUp()
        self.rejected_process = mock.Mock()
        self.consumer_config = helper.config.Data()
        self.consumer = Consumer(self.consumer_config, self.rejected_process)

        self.statsd_add_timing = mock.Mock()
        self.statsd_incr = mock.Mock()
        self.consumer._set_statsd(mock.Mock(incr=self.statsd_incr,
                                            add_timing=self.statsd_add_timing))

        self.sentry_client = mock.Mock()
        self.rejected_process.sentry_client = self.sentry_client
        self.sentry_client.tags = mock.Mock()

        self.channel = mock.Mock()
        self.channel.connection.ioloop = self.io_loop
        self.consumer._channel = self.channel

        self.http = mock.Mock()
        self.http_response = mock.Mock(code=200, request_time=0)
        self.consumer.http = self.http
        response = concurrent.Future()
        response.set_result(self.http_response)
        self.http.fetch.return_value = response

    @testing.gen_test
    def run_consumer(self, message_body=None, correlation_id=None):
        self.consumer._clear()
        self.consumer._message = mock.Mock()
        self.consumer._message.body = message_body or {}
        self.consumer._message.properties.correlation_id = correlation_id
        try:
            maybe_future = self.consumer.prepare()
            if concurrent.is_future(maybe_future):
                yield maybe_future
            if not self.consumer._finished:
                maybe_future = self.consumer.process()
                if concurrent.is_future(maybe_future):
                    yield maybe_future
        finally:
            if not self.consumer._finished:
                self.consumer.finish()

    def test_that_sentry_context_is_managed(self):
        self.run_consumer()
        self.sentry_client.tags_context.assert_called_once_with(
            {'service_invoked': 'httpbin'})
        self.sentry_client.tags.pop.assert_called_once_with(
            'service_invoked', None)

    def test_that_metrics_are_emitted(self):
        self.run_consumer()
        self.statsd_add_timing.assert_any_call(
            'http.fetch-stats.200', self.http_response.request_time)

    def test_that_timeout_result_in_processing_exceptions(self):
        self.http_response.code = 599
        with self.assertRaises(consumer.ProcessingException):
            self.run_consumer()
        self.statsd_add_timing.assert_any_call(
            'http.fetch-stats.599', self.http_response.request_time)

    def test_that_rate_limiting_result_in_processing_exceptions(self):
        self.http_response.code = 429
        with self.assertRaises(consumer.ProcessingException):
            self.run_consumer(mock.Mock())
        self.statsd_add_timing.assert_any_call(
            'http.fetch-stats.429', self.http_response.request_time)

    @testing.gen_test
    def test_that_call_http_service_accepts_body(self):
        yield self.consumer.call_http_service('fetch-stats', 'POST',
                                              body=mock.sentinel.body)
        self.http.fetch.assert_called_once_with(
            self.consumer.get_service_url('fetch-stats'),
            method='POST', body=mock.sentinel.body, raise_error=False)

    @testing.gen_test
    def test_that_call_http_service_jsonifies(self):
        yield self.consumer.call_http_service('fetch-stats', 'POST',
                                              json={'one': 1})
        self.http.fetch.assert_called_once_with(
            self.consumer.get_service_url('fetch-stats'),
            method='POST', body=json.dumps({'one': 1}).encode('utf-8'),
            headers={'Content-Type': 'application/json'}, raise_error=False)

    def test_that_socket_errors_result_in_processing_exception(self):
        future = concurrent.Future()
        future.set_exception(socket.error(42, 'message'))
        self.http.fetch.return_value = future

        with self.assertRaises(consumer.ProcessingException):
            self.run_consumer(mock.Mock())
        self.statsd_add_timing.assert_any_call(
            'http.fetch-stats.timeout', mock.ANY)
        self.statsd_incr.assert_any_call('errors.socket.42', 1)

    def test_that_correlation_id_from_message_is_passed_through(self):
        self.run_consumer(correlation_id=mock.sentinel.correlation_id)
        posn, kwargs = self.http.fetch.call_args_list[0]
        self.assertEqual(kwargs['headers']['Correlation-ID'],
                         mock.sentinel.correlation_id)

    def test_that_correlation_id_from_consumer_is_passed_through(self):
        setattr(self.consumer, '_correlation_id', mock.sentinel.correlation_id)
        self.run_consumer()
        posn, kwargs = self.http.fetch.call_args_list[0]
        self.assertEqual(kwargs['headers']['Correlation-ID'],
                         mock.sentinel.correlation_id)

    @testing.gen_test
    def test_that_raise_error_can_be_overridden(self):
        self.http_response.code = 500
        self.http_response.rethrow.side_effect = RuntimeError
        response = yield self.consumer.call_http_service(
            'fetch-stats', 'GET', raise_error=False)

        self.http.fetch.assert_called_once_with(
            self.consumer.get_service_url('fetch-stats'),
            method='GET', raise_error=False)
        self.assertIs(response, self.http_response)
