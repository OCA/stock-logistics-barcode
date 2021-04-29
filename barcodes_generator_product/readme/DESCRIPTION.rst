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
