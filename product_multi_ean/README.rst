.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

==========================
Multiple EAN13 on products
==========================

This module allow you to have multiple EAN13 on products.

Usage
=====

To use this module functionality, you need to enable product variants inside Sales or Inventory settings.
A list of EAN13 is available for each product with a priority, so a main EAN13 code is defined.
If a product has no variants, the product main barcode will automatically set to the main EAN13.


.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/150/10.0

Known issues
============

* The module unittest is carried over from version 8.0 and doesn't run successfully if the sales or stock modules are installed beforehand.

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/stock-logistics-barcode/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smashing it by providing a detailed and welcomed feedback.

Credits
=======

Contributors
------------

* Guewen Baconnier (Camptocamp)
* Roberto Lizana (Trey)
* Pedro M. Baeza
* Dionisius M. (Portcities)

Images
------

* Odoo Community Association: `Icon <https://github.com/OCA/maintainer-tools/blob/master/template/module/static/description/icon.svg>`_.


Maintainer
----------

.. image:: https://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: https://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

To contribute to this module, please visit https://odoo-community.org.
