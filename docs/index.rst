.. include:: ../README.rst

HTTP API Helpers
================
.. autoclass:: vetoes.service.HTTPServiceMixin
   :members:

Configuration Related
=====================
.. autoclass:: vetoes.config.FeatureFlagMixin
   :members:

.. autoclass:: vetoes.config.TimeoutConfigurationMixin
   :members:

Release History
===============

`0.4.0`_ (13-Apr-2017)
----------------------
- Added support to correctly translate ``user:password@host`` style
  URLs into ``auth_username`` and ``auth_password`` keyword parameters
  in :meth:`vetoes.service.HTTPServiceMixin.call_http_service`.

`0.3.0`_ (04-Apr-2017)
----------------------
- Updated to work against rejected 3.17
- Change :meth:`vetoes.service.HTTPServiceMixin.call_http_service` so that
  it honors timeouts set by :class:`vetoes.config.TimeoutConfigurationMixin`.

`0.2.0`_ (10-Jan-2017)
----------------------
- Added ``url`` keyword to
  :meth:`vetoes.service.HTTPServiceMixin.call_http_service`

`0.1.1`_ (06-Jan-2017)
----------------------
- Replaced readthedocs with pythonhosted.org.

`0.1.0`_ (06-Jan-2017)
----------------------
- Initial release including :class:`vetoes.service.HTTPServiceMixin`,
  :class:`vetoes.config.FeatureFlagMixin`, and
  :class:`vetoes.config.TimeoutConfigurationMixin`

.. _Next Release: https://github.aweber.io/edeliv/vetoes/compare/0.4.0...HEAD
.. _0.4.0: https://github.aweber.io/edeliv/vetoes/compare/0.3.0...0.4.0
.. _0.3.0: https://github.aweber.io/edeliv/vetoes/compare/0.2.0...0.3.0
.. _0.2.0: https://github.aweber.io/edeliv/vetoes/compare/0.1.1...0.2.0
.. _0.1.1: https://github.aweber.io/edeliv/vetoes/compare/0.1.0...0.1.1
.. _0.1.0: https://github.aweber.io/edeliv/vetoes/compare/0.0.0...0.1.0
