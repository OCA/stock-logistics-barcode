.. image:: https://img.shields.io/badge/licence-GPL--3-blue.svg
   :target: http://www.gnu.org/licenses/gpl-3.0-standalone.html
   :alt: License: GPL-3

=========================
Product barcode generator
=========================

This module will add a function which leads to an automatic generation of EAN13 for products

You will have to define the company default value (6 first numbers of EAN13) then the 6 next numbers of the sequence.

The 13rd is the control digit of the EAN13, this will be automatically computed.

The sequence to use to generate the ean13 can be specified at 3 levels (in the specified order):

* product
* category
* company

Usage
=====

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/150/8.0

Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OCA/stock-logistics-barcode/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and welcomed feedback
`here <https://github.com/OCA/stock-logistics-barcode/issues/new?body=module:%20product_barcode_generator%0Aversion:%208.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.


Credits
=======

Contributors
------------

* Mathieu VATEL <mathieu@julius.fr>
* Ivan Yelizariev <yelizariev@it-projects.info>
* Damien Crier <damien.crier@camptocamp.com>

Maintainer
----------

.. image:: https://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: https://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

To contribute to this module, please visit http://odoo-community.org.
