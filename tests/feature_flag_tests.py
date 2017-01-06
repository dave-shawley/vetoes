import unittest

import helper.config
import mock

from vetoes import config


class FeatureFlagMixinTests(unittest.TestCase):

    def test_that_flags_are_processed_during_initialize(self):
        settings = helper.config.Data({
            'features': {'on': 'on', 'off': 'false'}
        })
        consumer = config.FeatureFlagMixin(settings, mock.Mock())
        self.assertTrue(consumer.feature_flags['on'])
        self.assertFalse(consumer.feature_flags['off'])

    def test_that_invalid_flags_arg_ignored(self):
        settings = helper.config.Data({
            'features': {'one': 'not valid', 'two': None}
        })
        consumer = config.FeatureFlagMixin(settings, mock.Mock())
        self.assertEqual(consumer.feature_flags, {})
