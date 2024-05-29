Barcode interface for inventory operations
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To use the barcode interface on inventory:

#. Go to *Inventory > operations > Inventory Adjustments*.
#. Create new inventory with "Select products manually" option.
#. Start inventory.
#. Click to "Scan barcodes" smart button.
#. Start reading barcodes.

Barcode interface for picking operations
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
You can use the barcode interface in a picking or an operation type, the main
difference is that if you open the barcode interface from a picking, this
picking is locked and you read products for it.

To use the barcode interface on picking operations:

#. Go to *Inventory*.
#. Click on scanner button on any operation type.
#. Start reading barcodes.
#. The wizard will suggest pickings based on the scanned data (Product, quantity, lot, etc...)
#. Select a picking by clicking on the pin, and complete the desired operations.

To use the barcode interface on a picking:

#. Go to *Inventory > Transfers*.
#. Click to "Scan barcodes" smart button.
#. Start reading barcodes.

The barcode scanner interface has two operation modes. In both of them user
can scan:

#. Warehouse locations with barcode.
#. Product packaging with barcode.
#. Product with barcode.
#. Product Lots (The barcode is name field in this case).

Picking validation with a barcode scanner
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**The following example is based on the "Picking IN options".**

Requirements:

* Everything is based on the default configuration
* Must have a receipt picking with some products with barcodes

Follow the steps to validate a picking:

#. Go to *Inventory > Transfers*.
#. Open a **receipt** picking.
#. Click the "Scan barcodes" smart button.
#. The wizard interface to scan barcodes will show.
#. Start scanning the barcode of the currently selected product
    (Note: Scan the same barcode multiple times to add up quantity)
#. Repeat for every product in the picking paying attention to the currently selected product
    (The one in the yellow box)
#. Once it's all done, click on "Validate"

Automatic operation mode
~~~~~~~~~~~~~~~~~~~~~~~~

This is the default mode, all screen controls are locked to avoid scan into
fields.

The user only has to scan barcode in physical warehouse locations with a
scanner hardware, the interface read the barcode and do operations in this
order:

#. Try search a product, if found, is assigned to product_id field and creates
   or update inventory line with 1.0 unit. (If product has tracking by lots
   the interface wait for a lot to be scanned).
#. Try search a product packaging, if found, the product_id related is set,
   product quantities are updated and create or update inventory line with
   product quantities defined in the product packaging.
#. Try search a lot (The product is mandatory in this case so you first scan a
   product and then scann a lot), this lot field is not erased until that
   product change, so for each product scann the interface add or update a
   inventory line with this lot.
#. Try to search a location, if found the field location is set and next scan
   action will be done with this warehouse location.

If barcode has not found, when message is displayed you can create this lot
scanning the product.

Manual entry mode
~~~~~~~~~~~~~~~~~

You can change to "manual entry" to allow to select data without scanner
hardware, but hardware scanner still active on, so a use case would be when
user wants set quantities manually instead increment 1.0 unit peer scan action.

Scan logs
~~~~~~~~~

All scanned barcodes are saved into model.
Barcode scanning interface display 10 last records linked to model, the goal of
this log is show to user other reads with the same product and location done
by other users.
User can remove the last read scan.
