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

.. _Next Release: https://github.aweber.io/edeliv/vetoes/compare/0.2.0...HEAD
.. _0.2.0: https://github.aweber.io/edeliv/vetoes/compare/0.1.1...0.2.0
.. _0.1.1: https://github.aweber.io/edeliv/vetoes/compare/0.1.0...0.1.1
.. _0.1.0: https://github.aweber.io/edeliv/vetoes/compare/0.0.0...0.1.0
