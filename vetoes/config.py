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
