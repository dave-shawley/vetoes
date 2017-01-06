import json
import select
import socket

from rejected import consumer
from tornado import gen, httpclient, httputil


class HTTPServiceMixin(consumer.Consumer):
    """
    Mix this in to add the :meth:`.call_http_service` method.

    :keyword dict service_map: mapping from logical "function"
        to HTTP service.
    :param args: these are passed to :meth:`rejected.consumer.Consumer`
        as-is
    :param kwargs: these are passed to :meth:`rejected.consumer.Consumer`
        as-is

    The primary use of this mix-in is to make sending HTTP requests
    easier and safer.  The :meth:`.call_http_service` method uses the
    :meth:`.get_service_url` to build the request URL for a named
    **semantic function**, send the request to a specific **HTTP service**,
    and perform some "opinionated" processing on the response.  The
    separation of *semantic function* and *HTTP service* may seem a bit
    confusing at first.  They are used to provide concise logging and
    well-named metrics.  The semantic function describes the *action
    being performed* and the service is the *actor performing the action*.

    The mapping from *semantic function* to HTTP service is handled by
    the `service_map` passed into the initializer.  The mapping value is
    the **HTTP service** which is passed into :meth:`.get_service_url` to
    construct the request URL.

    .. attribute:: http_headers

       :class:`tornado.httputil.HTTPHeaders` instance of headers
       that are included in every request.  This set is empty.

    .. attribute:: http

       :class:`tornado.httpclient.AsyncHTTPClient` used to make
       requests.  The initializer sets the ``connect_timeout``
       and ``request_timeout`` in ``self.http.defaults``.

    """

    def __init__(self, *args, **kwargs):
        self.__service_map = kwargs.pop('service_map')
        super(HTTPServiceMixin, self).__init__(*args, **kwargs)
        self.http_headers = httputil.HTTPHeaders()
        self.http = httpclient.AsyncHTTPClient()
        self.http.defaults['connect_timeout'] = 5.0
        self.http.defaults['request_timeout'] = 30.0

    @gen.coroutine
    def call_http_service(self, function, method, *path, **kwargs):
        """
        Send a HTTP request to a service.

        :param str function: the function to invoke.  The service
            is determined based on the ``service_map`` established
            during initialization.
        :param str method: HTTP method to invoke.
        :param path: path elements to the HTTP resource.
        :keyword dict headers: optional set of headers to include
            in the message.  These are in addition to :attr:`http_headers`.
        :keyword json: optional body to send in the message.
            If this keyword is included, then the value is JSON encoded
            before being used as the body.
        :type json: dict or list
        :keyword bool raise_error: if this keyword is included and
            set to :data:`False`, then HTTP errors will be returned
            instead of raised as exceptions.
        :param kwargs: additional keyword arguments are passed to
            :meth:`tornado.httpclient.AsyncHTTPClient.fetch`.

        :returns: a :class:`tornado.httpclient.HTTPResponse` instance
        :rtype: tornado.httpclient.HTTPResponse

        :raises: tornado.httpclient.HTTPError if a HTTP error
            occurs
        :raises: rejected.consumer.ProcessingException if a low-level
            socket error occurs or a retry-able HTTP result is returned

        """
        headers = httputil.HTTPHeaders()
        cid = getattr(self, '_correlation_id', self.correlation_id)
        if cid:
            headers['Correlation-ID'] = cid
        headers.update(self.http_headers)
        headers.update(kwargs.pop('headers', {}))

        if 'json' in kwargs:
            body = json.dumps(kwargs.pop('json')).encode('utf-8')
            kwargs['body'] = body
            headers.setdefault('Content-Type', 'application/json')

        if headers:
            kwargs['headers'] = headers

        service = self.__service_map[function]
        self.sentry_client.tags_context({'service_invoked': service})
        url = self.get_service_url(service, *path,
                                   query_args=kwargs.pop('query_args', None))

        self.logger.debug('sending %s request to %s', method, url)
        raise_error = kwargs.pop('raise_error', True)
        start_time = self._channel.connection.ioloop.time()

        try:
            response = yield self.http.fetch(url, method=method,
                                             raise_error=False, **kwargs)
            self.statsd_add_timing(
                'http.{0}.{1}'.format(function, response.code),
                response.request_time)

        except (OSError, select.error, socket.error) as e:
            self.logger.exception('%s to %s failed', method, url)
            self.statsd_add_timing(
                'http.{0}.timeout'.format(function),
                self._channel.connection.ioloop.time() - start_time)
            self.statsd_incr(
                'errors.socket.{0}'.format(getattr(e, 'errno', 'unknown')))
            raise consumer.ProcessingException(
                '{0} connection failure - {1}'.format(service, e))

        finally:
            self.sentry_client.tags.pop('service_invoked', None)

        if response.code == 429:
            raise consumer.ProcessingException(
                '{0} is rate limiting requests'.format(service))

        if response.code == 599:
            raise consumer.ProcessingException(
                '{0} timed out for {1} to {2}'.format(service, method, url))

        if raise_error:
            response.rethrow()

        raise gen.Return(response)

    def get_service_url(self, service, *path, **kwargs):
        """
        Build a request URL for a specific service.

        :param str service: name of the service to invoke
        :param path: resource path elements
        :keyword query_args: optional query parameters to include in the URL
        :type query_args: dict or None

        :returns: the request URL
        :rtype: str

        .. note::

           You are required to override this method in your consumer.
           The base implementation simply raises an exception.

        """
        raise NotImplementedError
