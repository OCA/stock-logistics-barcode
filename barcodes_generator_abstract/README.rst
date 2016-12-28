.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

===========================================
Generate Barcodes for any Models (Abstract)
===========================================

This module expends Odoo functionality, allowing user to generate barcode
depending on a given barcode rule for any Model.

For exemple, a typical pattern for products is  "20.....{NNNDD}" that means
that:
* the EAN13 code will begin by '20'
* followed by 5 digits (named Barcode Base in this module)
* and after 5 others digits to define the variable price
* a 13 digit control

With this module, it is possible to:

* Affect a pattern (barcode.rule) to a model

* Define a Barcode base: 
    * manually, if the base of the barcode must be set by a user. (typically an
      internal code defined in your company)
    * automaticaly by a sequence, if you want to let Odoo to increment a
      sequence. (typical case of a customer number incrementation)

* Generate a barcode, based on the defined pattern and the barcode base

Installation
============

This module use an extra python library named 'viivakoodi' you should install
to make barcode generation works properly. 'viivakoodi' is a more active for of
'pyBarcode'.

``sudo pip install viivakoodi``

Configuration
=============

To configure this module, you need to:

* Go to Settings / Technical / Sequences & Identifiers / Barcode Nomenclatures
* Select a Nomenclature
* Create or select a rule

.. image:: /barcodes_generator_abstract/static/description/barcode_rule_tree.png

* For manual generation, set:
    * 'Base set Manually' in 'Generate Type'
    * Set the model

.. image:: /barcodes_generator_abstract/static/description/barcode_rule_form_manual.png

* For automatic generation, set:
    * 'Base managed by Sequence' in 'Generate Type'
    * Set the model
    * Generate a new sequence by button, or affect a existing one

.. image:: /barcodes_generator_abstract/static/description/barcode_rule_form_sequence.png

In all cases, padding will be computed automaticaly, based on the number
of '.' in the Barcode Pattern field.

Usage
=====

This module is an abstract module. You can configure Barcode Rule, but to
enable this feature, you need to install an extra module for a given model.
This repository provide 'barcodes_generator_product' and
'barcodes_generator_partner' module to generate barcode for product or partner
model.

Alternatively, you can develop a custom module for a custom model. See
'Inheritance' parts.

Try this module on Runbot

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/150/10.0

Inheritance
===========

If you want to generate barcode for another model, you can create a custom
module that inherits on 'barcodes_generator_abstract' and inherit your model
like that:

class MyModel(models.Model):
    _name = 'my.model'
    _inherit = ['my.model', 'barcode.generate.mixin']

class barcode_rule(models.Model):
    _inherit = 'barcode.rule'

    generate_model = fields.Selection(selection_add=[('my.model', 'My Model')])

Finally, you should inherit your model view adding buttons and fields.

Note
----

Your model should have a field 'barcode' defined.

Known issues / Roadmap
======================

1. On barcode.rule model, constraint and domain system could be set between
'type' and 'generate_model' fields.

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/stock-logistics-barcode/issues>`_. In case of trouble,
please check there if your issue has already been reported. If you spotted it
first, help us smashing it by providing a detailed and welcomed feedback.

Credits
=======

Images
------

* Icon of the module is based on the Oxygen Team work and is under LGPL licence:
  http://www.iconarchive.com/show/oxygen-icons-by-oxygen-icons.org.html

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

