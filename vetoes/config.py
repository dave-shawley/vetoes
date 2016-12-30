import distutils.util

from rejected import consumer


class FeatureFlagMixin(consumer.Consumer):
    """
    Mix this in to parse ``self.settings['features']``.

    Each flag in the ``features`` consumer setting is parsed using
    :func:`distutils.util.strtobool` and if it is parseable, then
    ``self.feature_flags[name]`` is set to the parsed result.

    For example, if your rejected configuration looks like:

    .. code-block:: yaml

       Application:
         Consumers:
           my-consumer:
             config:
               features:
                 frobinicate: on
                 defenestrate: no

    Then your consumer can expect ``feature_flags`` to be:

    .. code-block:: python

       feature_flags = {'frobinicate': True,
                        'defenestrate': False}

    """

    def __init__(self, *args, **kwargs):
        self.feature_flags = {}
        super(FeatureFlagMixin, self).__init__(*args, **kwargs)

    def initialize(self):
        super(FeatureFlagMixin, self).initialize()
        self._read_feature_flags()

    def _read_feature_flags(self):
        """Process ``self.settings['features']`` as a set of named flags."""
        flags = self.settings.get('features', {})
        for k, v in flags.items():
            try:
                parsed = bool(distutils.util.strtobool(v))
                self.feature_flags[k] = parsed
                self.logger.debug('feature %s is %s', k,
                                  'enabled' if parsed else 'disabled')

            except (AttributeError, ValueError) as e:
                self.logger.warning('failed to parse feature flag %s=%s - %r',
                                    k, v, e)


class TimeoutConfigurationMixin(consumer.Consumer):
    """
    Mix this in to parse ``self.settings['timeouts']``.

    The members from the timeouts dictionary is exposed by the
    :meth:`get_timeout` method.

    For example, if your rejected configuration looks like:

    .. code-block:: yaml

       Applications:
         Consumers:
           my-consumer:
             config:
               timeouts:
                 default: 0.1
                 dynamodb: 1.5

    Then your consumer can expect the following to hold true:

    .. code-block:: python

       self.get_timeout('dynamodb') == 1.5
       self.get_timeout('something-else') == 0.1

    If you omit the "default" key, then it will fallback to 0.5s.

    """

    def initialize(self):
        super(TimeoutConfigurationMixin, self).initialize()
        timeouts = self.settings.get('timeouts', {})
        self.__default_timeout = float(timeouts.get('default', '0.5'))

    def get_timeout(self, name, default=None):
        """
        Get the timeout named `name` from the consumer configuration.

        :param str name: the name of the timeout
        :param default: optional default value.  If this is omitted
            then the ``get_timeout('default', 0.5)`` will be returned
        :return: the appropriate timeout value in seconds
        :rtype: float

        """
        timeouts = self.settings.get('timeouts', {})
        return float(timeouts.get(name, default or self.__default_timeout))
