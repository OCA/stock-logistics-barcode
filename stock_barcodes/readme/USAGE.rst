Barcode interface for inventory operations
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Option 1: To use the barcode interface on inventory

  #. Go to *Inventory > operations > Inventory Adjustments*.
  #. Create new inventory with "Select products manually" option.
  #. Start inventory.
  #. Click to "Scan barcodes" smart button.
  #. Start reading barcodes.

Option 2: Use the barcode interface inventory directly from the Barcodes application
  #. Go to *Barcodes*.
  #. Select the *Inventory* option.

    .. image:: /stock_barcodes/static/src/img/inventory_barcode_action.png
       :height: 100
       :width: 200
       :alt: Inventory barcode action

  #. Start scanning barcodes.

Actions
  # Press the *+ Product* button to display the form for the new item.

    .. image:: /stock_barcodes/static/src/img/add_product.png
       :height: 100
       :width: 200
       :alt: Add product

  # When you select a product, a numeric field is displayed to add the quantity.

    .. image:: /stock_barcodes/static/src/img/form_add_product_quantity.png
       :height: 100
       :width: 200
       :alt: Add quantity product

  # When you press the button with the trash can icon, the values of the form are reset (except for the location) without closing it.

    .. image:: /stock_barcodes/static/src/img/form_add_product_reset.png
       :height: 100
       :width: 200
       :alt: Reset data form

  # When you press the *Clean values* button, all fields are reset and the form is closed.
  # When you press the *Confirm* button, the new item is added and the form is closed.
  # When the eye icon is closed, the created items greater than zero are displayed, and if not, those less than or equal to zero.

    .. image:: /stock_barcodes/static/src/img/list_items.png
       :height: 100
       :width: 200
       :alt: Reset data form

  # In the list, the trash can icon allows you to reset the quantity to zero and the edit icon allows you to change the item values.

    .. image:: /stock_barcodes/static/src/img/list_action_items.png
       :height: 100
       :width: 200
       :alt: Reset data form

  # The *Apply* button is only displayed if there are items with quantities greater than zero, regardless of whether they were scanned or entered manually; If you press all the defined quantities will be processed after defining the reason for the inventory adjustment and then the main barcode menu will be displayed.

    .. image:: /stock_barcodes/static/src/img/apply_inventory.png
       :height: 100
       :width: 200
       :alt: Apply inventory
    .. image:: /stock_barcodes/static/src/img/apply_inventory_reason.png
       :height: 100
       :width: 200
       :alt: Apply inventory reason


Barcode interface for picking operations
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
You can use the barcode interface in a picking or an operation type, the main
difference is that if you open the barcode interface from a picking, this
picking is locked and you read products for it.

To use the barcode interface on picking operations:

#. Go to *Inventory*.
#. Click on scanner button on any operation type.
#. Start reading barcodes.

Option 1: To use the barcode interface on a picking:

  #. Go to *Inventory > Transfers*.
  #. Click to "Scan barcodes" smart button.
  #. Start reading barcodes.

Option 2: Use the barcode interface picking directly from the Barcodes application
  #. Go to *Barcodes*.
  #. Select the option *OPERATIONS*.

    .. image:: /stock_barcodes/static/src/img/inventory_barcode_action.png
       :height: 100
       :width: 200
       :alt: Operation barcode action

  # Select the type of picking.
  # The pickings in ready status are displayed, select the one you want to start scanning.

    .. image:: /stock_barcodes/static/src/img/list_picking.png
       :height: 100
       :width: 200
       :alt: List picking

  #. Start scanning barcodes.

    .. image:: /stock_barcodes/static/src/img/barcode_interface_picking.png
       :height: 100
       :width: 200
       :alt: List picking

Actions
  # All the items that have been configured for the selected picking are listed.

    .. image:: /stock_barcodes/static/src/img/list_items_picking.png
       :height: 100
       :width: 200
       :alt: List picking

  # The edit icon in the list allows you to modify the data.

    .. image:: /stock_barcodes/static/src/img/list_items_picking_edit.png
       :height: 100
       :width: 200
       :alt: Edit picking

  # The button that contains a *+120* (in this case), allows you to define all the
    remaining quantities. Once defined, this button disappears and if you want to change the
    quantities, press the edit button.

    .. image:: /stock_barcodes/static/src/img/list_items_picking_quantity.png
       :height: 100
       :width: 200
       :alt: Quantity picking

  # If there is at least one item with a quantity already defined, an eye icon is displayed,
    which if closed shows the items and their quantities already scanned.

    .. image:: /stock_barcodes/static/src/img/list_items_picking_scanned.png
       :height: 100
       :width: 200
       :alt: Picking scanned

  # When you press the *Validate* button, a wizard will be displayed to confirm the action.
    If everything is correct, it is validated and you return to the picking list mentioned above.

    .. image:: /stock_barcodes/static/src/img/confirm_items_picking.png
       :height: 100
       :width: 200
       :alt: Picking scanned

  # If there is an item whose quantity is zero, a wizard will be displayed after the one mentioned
    above, to confirm if you want to process all the quantities. If positive, you will proceed
    and be directed to the list mentioned above in the previous point.

    .. image:: /stock_barcodes/static/src/img/confirm_all_quantity_items_picking.png
       :height: 100
       :width: 200
       :alt: Picking scanned

  # Press the *+ Product* button to display the form for the new item.

    .. image:: /stock_barcodes/static/src/img/add_product.png
       :height: 100
       :width: 200
       :alt: Add product

  # When you select a product, a numeric field is displayed to add the quantity.

    .. image:: /stock_barcodes/static/src/img/form_add_product_quantity.png
       :height: 100
       :width: 200
       :alt: Add quantity product

  # When you press the button with the trash can icon, the values of the form are reset (except for the location) without closing it.

    .. image:: /stock_barcodes/static/src/img/form_add_product_reset.png
       :height: 100
       :width: 200
       :alt: Reset data form

  # When you press the *Clean values* button, all fields are reset and the form is closed.
  # When you press the *Confirm* button, the new item is added and the form is closed.
  # When adding the new item all the quantities are assigned to it, if you want to modify it, press the edit icon.

The barcode scanner interface has two operation modes. In both of them user
can scan:

#. Warehouse locations with barcode.
#. Product packaging with barcode.
#. Product with barcode.
#. Product Lots (The barcode is name field in this case).


Automatic operation mode
~~~~~~~~~~~~~~~~~~~~~~~~

This is the default mode, all screen controls are locked to avoid scan into
fields.

The user only has to scan barcode in physical warehouse locations with a
scanner hardward, the interface read the barcode and do operations in this
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
hardware, but hardward scanner still active on, so a use case would be when
user wants set quantities manually instead increment 1.0 unit peer scan action.

Scan logs
~~~~~~~~~

All scanned barcodes are saved into model.
Barcode scanning interface display 10 last records linked to model, the goal of
this log is show to user other reads with the same product and location done
by other users.
User can remove the last read scan.

Barcode interface for barcode actions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
To use the barcode interface for actions:

#. Go to *Inventory > Configuration > Barcode Actions*.
#. Create a new barcode action and configure the barcode.

.. image:: /stock_barcodes/static/src/img/create_barcode_action.png
   :height: 100
   :width: 200
   :alt: Print barcodes

#. Select the barcode actions you want to use, a button (PRINT BARCODES) will appear that allows you to print the configured barcodes to PDF.

.. image:: /stock_barcodes/static/src/img/print_barcodes.png
   :height: 100
   :width: 200
   :alt: Print barcodes

#. Go to *Barcodes*.
#. Start scanning barcodes from actions.
