.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :alt: License: AGPL-3

GS1 Barcodes
============

This module provides an API to decoding the content of structured barcodes
like GS1-128 or GS1-Datamatrix.

GS1-128 (formerly known as UCC-128, EAN 128 or UCC/EAN-128), and GS1-Datamatrix
are standards for encoding item identification and logistics data.
Physically, GS1-128 is represented as a 1-dimension Code-128 barcode and
GS1-Datamtrix is represented as a 2-dimensions Datamatrix barcode.

When those barcodes are read, their content can be decode into multiple values
using a set of standard "Application Identifiers". For example, most pharmacy
items have a GS1-Datamatrix barcode containg their GTIN, lot number and
expiry date.

This module does not directly allow you to print or scan barcodes.
Instead, the focus of this module is on decoding the data contained in
barcodes. To this end, it provides objects to fine-tune the Application
Identifiers and the associated data types.

Configuration
=============

To configure the Application Identifiers and the associated data types, go to
*Sales -> Settings -> Product Categories & Attributes ->
GS1-128/GS1-Datamatrix Decoding*

You can configure the barcode string separator and prefix in the System
parameters. Use *None* to indicate a null prefix.

Usage
=====

You can use the functionality provided by this module in your own customization
or other OCA modules.

For further information, please visit:

* https://www.odoo.com/forum/help-1


Known issues / Roadmap
======================

Group separator
---------------
When an "Application Identifiers" has variable-length data,
the barcodes must contain a special character (<GS>, group separator)
but as this is not an ASCII character. Some barcode readers will not include
this character: decoding the structured data will then be impossible. Other
readers will translate GS1 to ASCII character 29, but this character is not
printable, and some applications may not record it. Yet other readers will
let you configure how to map <GS>, which may help improve compatibility.

Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OCA/{stock-logistics-barcode}/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and welcomed feedback
`here <https://github.com/OCA/{stock-logistics-barcode}/issues/new?body=module:%20{base_gs1_barcode}%0Aversion:%20{version}%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.

Credits
=======

Numérigraphe (http://numerigraphe.com)

Contributors
------------

* Lionel Sausin <ls@numerigraphe.fr>
* Stefan Rijnhart <stefan@therp.nl>

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
