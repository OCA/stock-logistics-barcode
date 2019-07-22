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
