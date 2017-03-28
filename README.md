[![Build Status](https://travis-ci.org/OCA/stock-logistics-barcode.svg?branch=9.0)](https://travis-ci.org/OCA/stock-logistics-barcode)
[![Coverage Status](https://img.shields.io/coveralls/OCA/stock-logistics-barcode.svg)](https://coveralls.io/r/OCA/stock-logistics-barcode?branch=9.0)

Odoo Stock Logistic Barcode
===========================


This project aims to deal with modules related to the management of barcode in a generic way. You'll find modules that:

 - Allow to generate bar code each time a object is created
 - Setup bar code on object
 - Print bar code
 - Search and use them with a barcode scanner

Please don't hesitate to suggest one of your module to this project. Also, you may want to have a look on those other projects here:

 - https://github.com/OCA/stock-logistics-tracking
 - https://github.com/OCA/stock-logistics-workflow
 - https://github.com/OCA/stock-logistics-warehouse

[//]: # (addons)

Available addons
----------------
addon | version | summary
--- | --- | ---
[barcodes_generator_abstract](barcodes_generator_abstract/) | 9.0.1.0.0 | Generate Barcodes for Any Models
[barcodes_generator_partner](barcodes_generator_partner/) | 9.0.1.0.0 | Generate Barcodes for Partners
[barcodes_generator_product](barcodes_generator_product/) | 9.0.1.0.0 | Generate Barcodes for Products (Templates and Variants)
[stock_scanner](stock_scanner/) | 9.0.1.0.0 | Allows managing barcode readers with simple scenarios
[stock_scanner_inventory](stock_scanner_inventory/) | 9.0.1.0.0 | Stock Scanner Inventory
[stock_scanner_location_info](stock_scanner_location_info/) | 9.0.1.0.0 | Stock Scanner Location Info
[stock_scanner_receipt](stock_scanner_receipt/) | 9.0.1.0.0 | Stock Scanner Receipt
[stock_scanner_shipping](stock_scanner_shipping/) | 9.0.1.0.0 | Stock Scanner Shipping


Unported addons
---------------
addon | version | summary
--- | --- | ---
[barcode_link](barcode_link/) | 1.0 (unported) | Barcode link Module
[base_gs1_barcode](base_gs1_barcode/) | 1.0 (unported) | Decoding API for GS1-128 (aka UCC/EAN-128) and GS1-Datamatrix
[product_multi_ean](product_multi_ean/) | 1.2 (unported) | Multiple EAN13 on products
[tr_barcode](tr_barcode/) | 1.1.4 (unported) | TR Barcode
[tr_barcode_config](tr_barcode_config/) | 1.1.1 (unported) | Barcode configuration Module
[tr_barcode_field](tr_barcode_field/) | 1.1 (unported) | Barcode field Module
[tr_barcode_on_picking](tr_barcode_on_picking/) | 1.1 (unported) | Barcode for pickings
[tr_barcode_on_prodlots](tr_barcode_on_prodlots/) | 1.1 (unported) | Barcode for production lots
[tr_barcode_on_product](tr_barcode_on_product/) | 1.1 (unported) | Barcode for product
[tr_barcode_on_tracking](tr_barcode_on_tracking/) | 1.1 (unported) | Barcode for tracking

[//]: # (end addons)
