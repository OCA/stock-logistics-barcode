This module allows barcode nomenclatures to use regex groups to capture a part of a barcode.

Odoo's default ``barcodes`` module uses regex to match the barcode against the nomenclature rules, but in case of a match, it passes the full string to the ``on_barcode_scanned`` method.

With this module, we can use regex groups to specify which part of the barcode we want. For example, when a barcode looks like this:

::

    PRODUCT X1234 SERIAL 12345

We can define a regex to capture the serial number only, looking like this:

::

    PRODUCT [a-zA-Z0-9-]* SERIAL ([a-zA-Z0-9]*)

As an added feature, we can specify the Odoo models that a certain rule should apply to. Let us say that in the above case, we make a rule for product, but also for serial. We want the 'serial' rule to fire for ``stock.pack.operation`` operations, but the 'product' rule to fire for ``stock.picking`` operations, while scanning the same barcode, so, we make two rules, and configure a different model for each.
