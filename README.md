
[![Runboat](https://img.shields.io/badge/runboat-Try%20me-875A7B.png)](https://runboat.odoo-community.org/builds?repo=OCA/stock-logistics-barcode&target_branch=13.0)
[![Pre-commit Status](https://github.com/OCA/stock-logistics-barcode/actions/workflows/pre-commit.yml/badge.svg?branch=13.0)](https://github.com/OCA/stock-logistics-barcode/actions/workflows/pre-commit.yml?query=branch%3A13.0)
[![Build Status](https://github.com/OCA/stock-logistics-barcode/actions/workflows/test.yml/badge.svg?branch=13.0)](https://github.com/OCA/stock-logistics-barcode/actions/workflows/test.yml?query=branch%3A13.0)
[![codecov](https://codecov.io/gh/OCA/stock-logistics-barcode/branch/13.0/graph/badge.svg)](https://codecov.io/gh/OCA/stock-logistics-barcode)
[![Translation Status](https://translation.odoo-community.org/widgets/stock-logistics-barcode-13-0/-/svg-badge.svg)](https://translation.odoo-community.org/engage/stock-logistics-barcode-13-0/?utm_source=widget)

<!-- /!\ do not modify above this line -->

# Odoo Stock Logistic Barcode

This project aims to deal with modules related to the management of barcode in a generic way. You'll find modules that:

 - Allow to generate bar code each time a object is created
 - Setup bar code on object
 - Print bar code
 - Search and use them with a barcode scanner

Please don't hesitate to suggest one of your module to this project. Also, you may want to have a look on those other projects here:

 - https://github.com/OCA/stock-logistics-tracking
 - https://github.com/OCA/stock-logistics-workflow
 - https://github.com/OCA/stock-logistics-warehouse

<!-- /!\ do not modify below this line -->

<!-- prettier-ignore-start -->

[//]: # (addons)

Available addons
----------------
addon | version | maintainers | summary
--- | --- | --- | ---
[barcodes_generator_abstract](barcodes_generator_abstract/) | 13.0.1.0.0 |  | Generate Barcodes for Any Models
[barcodes_generator_location](barcodes_generator_location/) | 13.0.1.0.0 |  | Generate Barcodes for Stock Locations
[barcodes_generator_product](barcodes_generator_product/) | 13.0.1.0.0 |  | Generate Barcodes for Products (Templates and Variants)
[base_gs1_barcode](base_gs1_barcode/) | 13.0.1.1.0 |  | Decoding API for GS1-128 (aka UCC/EAN-128) and GS1-Datamatrix
[product_gtin](product_gtin/) | 13.0.1.0.0 |  | This module provides checks and management to EAN codes
[product_multi_barcode](product_multi_barcode/) | 13.0.1.1.0 |  | Multiple barcodes on products
[stock_barcodes](stock_barcodes/) | 13.0.2.2.6 |  | It provides read barcode on stock operations.
[stock_barcodes_automatic_entry](stock_barcodes_automatic_entry/) | 13.0.1.0.1 | [![AdriaGForgeFlow](https://github.com/AdriaGForgeFlow.png?size=30px)](https://github.com/AdriaGForgeFlow) | This module will automatically trigger the click event on a button with the class 'barcode-automatic-entry' after a barcode scanned has been processed.
[stock_barcodes_gs1](stock_barcodes_gs1/) | 13.0.2.0.2 |  | It provides read GS1 barcode on stock operations.
[stock_barcodes_gs1_expiry](stock_barcodes_gs1_expiry/) | 13.0.1.0.1 |  | It provides read expiry dates from GS1 barcode on stock operations.
[stock_barcodes_move_location](stock_barcodes_move_location/) | 13.0.1.0.1 |  | It provides read barcode on stock operations.
[stock_picking_product_barcode_report](stock_picking_product_barcode_report/) | 13.0.2.2.0 | [![CarlosRoca13](https://github.com/CarlosRoca13.png?size=30px)](https://github.com/CarlosRoca13) | It provides a wizard to select how many barcodes print.
[stock_picking_product_barcode_report_secondary_unit](stock_picking_product_barcode_report_secondary_unit/) | 13.0.1.1.0 | [![CarlosRoca13](https://github.com/CarlosRoca13.png?size=30px)](https://github.com/CarlosRoca13) | Set by default the maximum quantity of labels to print.

[//]: # (end addons)

<!-- prettier-ignore-end -->

## Licenses

This repository is licensed under [AGPL-3.0](LICENSE).

However, each module can have a totally different license, as long as they adhere to Odoo Community Association (OCA)
policy. Consult each module's `__manifest__.py` file, which contains a `license` key
that explains its license.

----
OCA, or the [Odoo Community Association](http://odoo-community.org/), is a nonprofit
organization whose mission is to support the collaborative development of Odoo features
and promote its widespread use.
