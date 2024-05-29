Barcodes Actions
~~~~~~~~~~~~~~~~

The Barcode Actions are selectable from the "Barcode" interface.

These can be personalized by selecting an action window, and apply context.

The purpose of the action is to direct the user towards the records of the models which have integrations with barcodes.

Barcodes Options
~~~~~~~~~~~~~~~~

Options are used to describe how the barcode interface should behave.

To properly configure these options, look out for the following fields:

* Code: refers to the code in the Picking Type

* Behaviour Settings: check the 'Help Tooltip' by hovering on the fields

* Steps to Scan:

  * Step: Order of the actions to be executed
  * Name: Significant name to be visualized in the alert on the top of the screen for any information related to that field
  * Field Name: Name of the field of the wizard (e.g. For pickings the field are in `stock.barcodes.read.picking`) which will be filled
  * Filled Default: Useful to automatically fill values based on the move line (Can be used on locations, product, lot, quantity, etc...)
  * Forced: Adds a layer of validation, that doesn't let the user proceed until that field is entered correctly
  * To Scan: This field will be filled using a barcode scanner, after the scan the barcode will be processed by a method named `_process_barcode_<field_name>()`
  * Required: Every required field will be checked before confirmation
  * Clean After Done: These fields will be cleaned after confirmation

