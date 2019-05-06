To use this module you need a barcode scanner.

In Odoo, click on the scan button in the picking form:

.. image:: ../static/description/stock_picking_scan.png
    :alt: Stock Picking Scan Button

Scan the Serial Number Barcode. If the SN is in the system a success message
will be displayed. Otherwise, an error message will appear.

* Successful scan:

.. image:: ../static/description/scan_successful.png
    :alt: Scan Successful

* Wrong SN:

.. image:: ../static/description/scan_error.png
    :alt: Scan Error

After scanning a product, it will be added to the picking with the corresponding
scanned serial number.

.. image:: ../static/description/stock_picking_result.png
    :alt: Scan Result