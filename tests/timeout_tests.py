import unittest

import helper.config
import mock

from vetoes import config


class TimeoutConfigurationTests(unittest.TestCase):

    def test_that_default_timeout_is_500ms(self):
        settings = helper.config.Data({})
        consumer = config.TimeoutConfigurationMixin(settings, mock.Mock())
        self.assertAlmostEqual(consumer.get_timeout('whatever'), 0.5)

    def test_that_default_timeout_is_configurable(self):
        settings = helper.config.Data({'timeouts': {'default': '1.0'}})
        consumer = config.TimeoutConfigurationMixin(settings, mock.Mock())
        self.assertAlmostEqual(consumer.get_timeout('whatever'), 1.0)

    def test_that_named_timeout_works(self):
        settings = helper.config.Data({'timeouts': {'whatever': '1.0'}})
        consumer = config.TimeoutConfigurationMixin(settings, mock.Mock())
        self.assertAlmostEqual(consumer.get_timeout('whatever'), 1.0)
