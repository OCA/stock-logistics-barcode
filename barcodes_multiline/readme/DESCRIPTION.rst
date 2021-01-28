This module allows the scanning of barcodes that span multiple lines eg:

::

    PRODUCT: X1234
    SERIALNUMBER: 123456
    PRODUCTION DATE: 2020-12-01

Without this module, Odoo recognizes characters ``\n``, ``\r`` and ``\t`` as characters that signal the end of a barcode. A 50 ms timeout without keyboard input also ends the barcode. Thus, above barcode would be split up into three separate barcodes.

With this module installed, special characters no longer signal the end of barcode, only the 50 ms timeout. Thus, above barcode would be fed to the ``on_barcode_scanned`` method as a whole, to be processed in full.
