This module expands Odoo functionality, allowing user to generate barcode
depending on a given barcode rule for Stock Locations.

For example, a typical pattern for partners is  "042........." that means
that:
* the EAN13 code will begin by '042'
* followed by 0 digits (named Barcode Base in this module)
* a 13 digit control

With this module, it is possible to:

* Assign a pattern (barcode.rule) to a stock.location

* Define a Barcode base:
    * manually, if the base of the barcode must be set by a user. (typically an
      internal code defined in your company)
    * automatically by a sequence, if you want to let Odoo to increment a
      sequence. (typical case of a customer number incrementation)

* Generate a barcode, based on the defined pattern and the barcode base
