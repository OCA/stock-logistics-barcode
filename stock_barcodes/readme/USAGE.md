## Barcode Configuration for Warehouse Locations

> 1. To see the following menu you must have the permission assigned: *Manage Multiple Stock Locations*.

> ![Warehouse location access](/stock_barcodes/static/src/img/access_menu_warehouse_location.png)

> 2. Go to *Inventory \> Configuration \> Locations*.
> 3. Select the location you want to associate with the barcode.
> 4. Go to the Barcode field and assign the corresponding field.

> ![Warehouse location barcode](/stock_barcodes/static/src/img/barcode_warehouse_location.png)

> 5. Save the data.

## Barcode Configuration for Product Packings

> 1. To see the following menu you must have the permission assigned: *Manage Product Packaging*.

> ![Product packaging barcode](/stock_barcodes/static/src/img/access_menu_product_packaging.png)

> 2. Go to *Inventory \> Configuration \> Product Packings*.
> 3. Create a new or select product packaging.
> 4. Go to the Barcode field and assign the corresponding field.

> ![Product packaging barcode](/stock_barcodes/static/src/img/barcode_product_packaging.png)

> 5. Save the data.

## Barcode Configuration for Product

> 1. Go to *Inventory \> Products \> Products*.
> 2. Create a new product.
> 3. Go to the Barcode field and assign the corresponding field.

> ![Product packaging barcode](/stock_barcodes/static/src/img/barcode_product.png)

> 4. Save the data.

## Barcode Configuration for Product lot

> 1. Go to *Inventory \> Products \> Lots/Serial Numbers*.
> 2. Create a new lot.
> 3. In this case, the barcode matches the lot name, so when you name the lot, you already have the barcode configured.

> ![Product lot barcode](/stock_barcodes/static/src/img/barcode_product_lot.png)

> 4. Save the data.

## Barcode interface for inventory operations

Please note that the picking is marked with the entire
quantity requested by default in the ready state.


Option 1: To use the barcode interface on inventory

> 1. Go to *Inventory \> operations \> Inventory Adjustments*.
> 2. Create new inventory with "Select products manually" option.
> 3. Start inventory.
> 4. Click to "Scan barcodes" smart button.
> 5. Start reading barcodes.

Option 2: Use the barcode interface inventory directly from the Barcodes application

1. Go to *Barcodes*.
2. Select the *Inventory* option.

> ![Inventory barcode action](/stock_barcodes/static/src/img/inventory_barcode_action.png)

1. Start scanning barcodes.

Actions
\# Press the *+ Product* button to display the form for the new item.

> ![Add product](/stock_barcodes/static/src/img/add_product.png)

\# When you select a product, a numeric field is displayed to add the
quantity.

> ![Add quantity product](/stock_barcodes/static/src/img/form_add_product_quantity.png)

\# When you press the button with the trash can icon, the values of the
form are reset (except for the location) without closing it.

> ![Reset data form](/stock_barcodes/static/src/img/form_add_product_reset.png)

\# When you press the *Clean values* button, all fields are reset and
the form is closed. \# When you press the *Confirm* button, the new item
is added and the form is closed. \# When the eye icon is closed, the
created items greater than zero are displayed, and if not, those less
than or equal to zero.

> ![Reset data form](/stock_barcodes/static/src/img/list_items.png)

\# In the list, the trash can icon allows you to reset the quantity to
zero and the edit icon allows you to change the item values.

> ![Reset data form](/stock_barcodes/static/src/img/list_action_items.png)

\# The *Apply* button is only displayed if there are items with
quantities greater than zero, regardless of whether they were scanned or
entered manually; If you press all the defined quantities will be
processed after defining the reason for the inventory adjustment and
then the main barcode menu will be displayed.

> ![Apply inventory](/stock_barcodes/static/src/img/apply_inventory.png)
>
> ![Apply inventory reason](/stock_barcodes/static/src/img/apply_inventory_reason.png)

## Barcode interface for picking operations

You can use the barcode interface in a picking or an operation type, the
main difference is that if you open the barcode interface from a
picking, this picking is locked and you read products for it.

To use the barcode interface on picking operations:

1. Go to *Inventory*.
2. Click on scanner button on any operation type.
3. Start reading barcodes.

Option 1: To use the barcode interface on a picking:

> 1. Go to *Inventory \> Transfers*.
> 2. Click to "Scan barcodes" smart button.
> 3. Start reading barcodes.

Option 2: Use the barcode interface picking directly from the Barcodes application

1. Go to *Barcodes*.
2. Select the option *OPERATIONS*.

> ![Operation barcode action](/stock_barcodes/static/src/img/inventory_barcode_action.png)

\# Select the type of picking. \# The pickings in ready status are
displayed, select the one you want to start scanning.

> ![List picking](/stock_barcodes/static/src/img/list_picking.png)

1. Start scanning barcodes.

> ![List picking](/stock_barcodes/static/src/img/barcode_interface_picking.png)

Actions
\# All the items that have been configured for the selected picking are
listed.

> ![List picking](/stock_barcodes/static/src/img/list_items_picking.png)

\# The edit icon in the list allows you to modify the data.

> ![Edit picking](/stock_barcodes/static/src/img/list_items_picking_edit.png)

\# The button that contains a *+120* (in this case), allows you to define all the
remaining quantities. Once defined, this button disappears and if you
want to change the quantities, press the edit button.

![Quantity picking](/stock_barcodes/static/src/img/list_items_picking_quantity.png)

\# If there is at least one item with a quantity already defined, an eye icon is displayed,
which if closed shows the items and their quantities already scanned.

![Picking scanned](/stock_barcodes/static/src/img/list_items_picking_scanned.png)

\# When you press the *Validate* button, a wizard will be displayed to confirm the action.
If everything is correct, it is validated and you return to the picking
list mentioned above.

![Picking scanned](/stock_barcodes/static/src/img/confirm_items_picking.png)

\# If there is an item whose quantity is zero, a wizard will be displayed after the one mentioned
above, to confirm if you want to process all the quantities. If
positive, you will proceed and be directed to the list mentioned above
in the previous point.

![Picking scanned](/stock_barcodes/static/src/img/confirm_all_quantity_items_picking.png)

\# Press the *+ Product* button to display the form for the new item.

> ![Add product](/stock_barcodes/static/src/img/add_product.png)

\# When you select a product, a numeric field is displayed to add the
quantity.

> ![Add quantity product](/stock_barcodes/static/src/img/form_add_product_quantity.png)

\# When you press the button with the trash can icon, the values of the
form are reset (except for the location) without closing it.

> ![Reset data form](/stock_barcodes/static/src/img/form_add_product_reset.png)

\# When you press the *Clean values* button, all fields are reset and
the form is closed. \# When you press the *Confirm* button, the new item
is added and the form is closed. \# When adding the new item all the
quantities are assigned to it, if you want to modify it, press the edit
icon.

The barcode scanner interface has two operation modes. In both of them
user can scan:

1. Warehouse locations with barcode.
2. Product packaging with barcode.
3. Product with barcode.
4. Product Lots (The barcode is name field in this case).

## Automatic operation mode

This is the default mode, all screen controls are locked to avoid scan
into fields.

The user only has to scan barcode in physical warehouse locations with a
scanner hardward, the interface read the barcode and do operations in
this order:

1. Try search a product, if found, is assigned to product_id field and
   creates or update inventory line with 1.0 unit. (If product has
   tracking by lots the interface wait for a lot to be scanned).
2. Try search a product packaging, if found, the product_id related is
   set, product quantities are updated and create or update inventory
   line with product quantities defined in the product packaging.
3. Try search a lot (The product is mandatory in this case so you first
   scan a product and then scann a lot), this lot field is not erased
   until that product change, so for each product scann the interface
   add or update a inventory line with this lot.
4. Try to search a location, if found the field location is set and
   next scan action will be done with this warehouse location.

If barcode has not found, when message is displayed you can create this
lot scanning the product.

## Manual entry mode

You can change to "manual entry" to allow to select data without scanner
hardware, but hardward scanner still active on, so a use case would be
when user wants set quantities manually instead increment 1.0 unit peer
scan action.

## Scan logs

All scanned barcodes are saved into model. Barcode scanning interface
display 10 last records linked to model, the goal of this log is show to
user other reads with the same product and location done by other users.
User can remove the last read scan.

## Barcode interface for barcode actions

To use the barcode interface for actions:

1. Go to *Inventory \> Configuration \> Barcode Actions*.
2. Create a new barcode action and configure the barcode.

![Print barcodes](/stock_barcodes/static/src/img/create_barcode_action.png)

1. Select the barcode actions you want to use, a button (PRINT
   BARCODES) will appear that allows you to print the configured
   barcodes to PDF.

![Print barcodes](/stock_barcodes/static/src/img/print_barcodes.png)

1. Go to *Barcodes*.
2. Start scanning barcodes from actions.
