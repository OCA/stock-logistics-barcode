.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

=======================================================
Generate Barcodes for Products (Templates and Variants)
=======================================================

This module expands Odoo functionality, allowing user to generate barcode
depending on a given barcode rule for Products.

For example, a typical pattern for products is  "20.....{NNNDD}" that means
that:
* the EAN13 code will begin by '20'
* followed by 5 digits (named Barcode Base in this module)
* and after 5 others digits to define the variable price
* a 13 digit control

With this module, it is possible to:

* Assign a pattern (barcode.rule) to a product.product

* Define a Barcode base: 
    * manually, if the base of the barcode must be set by a user. (typically an
      internal code defined in your company)
    * automaticaly by a sequence, if you want to let Odoo to increment a
      sequence. (typical case of a customer number incrementation)

* Generate a barcode, based on the defined pattern and the barcode base

Configuration
=============

To configure this module, see the 'Configuration' Section of the description
of the module 'barcodes_generator_abstract'

Usage
=====

To use this module, you need to:

* Go to a Product form (or a template form):

1 for manual generation
    * Set a Barcode Rule
    * Set a Barcode Base
    * click on the button 'Generate Barcode (Using Barcode Rule)'

.. image:: /barcodes_generator/static/description/product_template_manual_generation.png

2 for automatic generation
    * Set a Barcode Rule
    * click on the button 'Generate Base (Using Sequence)'
    * click on the button 'Generate Barcode (Using Barcode Rule)'


Try this module on Runbot

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/150/10.0

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/stock-logistics-barcode/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smash it by providing detailed and welcomed feedback.

Credits
=======

Images
------

* Icon of the module is based on the Oxygen Team work and is under LGPL licence:
  http://www.iconarchive.com/show/oxygen-icons-by-oxygen-icons.org.html
* Product tag by `Zlatko Najdenovski <https://www.iconfinder.com/zlaten>`_ and is licensed
  under `CC BY 3.0 <https://creativecommons.org/licenses/by/3.0/>`_.

Contributors
------------

* Sylvain LE GAL (https://twitter.com/legalsylvain)
* Dave Lasley <dave@laslabs.com>

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

