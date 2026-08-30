The barcode scan screens recognize, in both free and guided mode:

1. Warehouse locations (barcode field).
2. Product packagings (barcode field).
3. Products (barcode field).
4. Lots / serial numbers (the barcode is the lot name).
5. Packages (matched by name).

A bell sound confirms a successful scan and an error sound signals a
rejected one. Status messages under the barcode field explain what the
screen is waiting for and why a scan was rejected. The *Manual* button
toggles manual entry to type values without a scanner.

## Barcode interface for picking operations

You can open the scan screen from three places:

1. **Barcodes main menu** (app *Barcodes*): select an operation tile,
   then pick one of the ready transfers from the list.

   ![Operation barcode action](/stock_barcodes/static/src/img/inventory_barcode_action.png)

   ![List picking](/stock_barcodes/static/src/img/list_picking.png)

2. **An operation type card** in *Inventory > Overview* (scanner
   button): scan products for any ready picking of that type.
3. **A specific transfer** (*Scan barcodes* button in
   *Inventory > Transfers*): the picking is locked and every scan
   applies to it.

   ![Barcode interface picking](/stock_barcodes/static/src/img/barcode_interface_picking.png)

### Free mode

Scan in any order; the screen reacts to the kind of barcode read:

- **Product**: adds 1 unit (or waits for a lot if the product is
  tracked). The source location is resolved automatically from the
  pending reserved lines.
- **Packaging**: selects the product and adds the packaging quantity.
- **Lot**: scan the product first when several lots share the same name.
  When *fill fields from lot* is active, scanning a lot fills product,
  package, owner and location from the available stock.
- **Package**: fills all fields from the package content.
- **Location**: sets the source (or destination, per configuration) for
  the following scans.

Quantities beyond the picking demand or beyond available stock are not
written silently: the screen asks for confirmation (*force done*) or
rejects the scan, depending on the option group.

### Guided mode

The screen shows the next pending move (product, lot, quantities,
locations) and guides the operator step by step (e.g. *Scan Source*,
then *Scan Product, Lot*). Scanning something different from what is
expected is rejected with an explicit message (*Wrong product*, *Wrong
lot*, *Wrong location*).

In the pending moves list you can:

- Jump to another line (arrows or tapping a card).

  ![List items picking](/stock_barcodes/static/src/img/list_items_picking.png)

- Edit a line with the pencil icon.

  ![Edit picking](/stock_barcodes/static/src/img/list_items_picking_edit.png)

- Put the whole remaining quantity with the *+N* button (e.g. *+120*).
  Once defined, this button disappears; use the edit icon to change the
  quantity.

  ![Quantity picking](/stock_barcodes/static/src/img/list_items_picking_quantity.png)

- Show the lines already scanned with the eye icon.

  ![Picking scanned](/stock_barcodes/static/src/img/list_items_picking_scanned.png)

- Decide the backorder behavior per line when quantities are incomplete
  (create backorder / no backorder / keep pending).

### Validation

The *Validate* button confirms the transfer using the scanned
quantities. A wizard is displayed to confirm the action; after
validation you return to the ready-pickings list.

![Confirm items picking](/stock_barcodes/static/src/img/confirm_items_picking.png)

If some lines have no quantity, the standard confirmation wizard asks
whether to process all quantities.

![Confirm all quantities](/stock_barcodes/static/src/img/confirm_all_quantity_items_picking.png)

With *Auto put in pack* enabled, unpacked lines are packed automatically
before validating.

### Extra products, new lots and packagings

- Press the *+ Product* button to add an item not in the demand (when
  the option group allows non-demanded products).

  ![Add product](/stock_barcodes/static/src/img/add_product.png)

  When you select a product, a numeric field is displayed to add the
  quantity.

  ![Add quantity product](/stock_barcodes/static/src/img/form_add_product_quantity.png)

  The trash can icon resets the form values (except the location)
  without closing it; *Clean values* resets everything and closes the
  form; *Confirm* adds the new item.

  ![Reset data form](/stock_barcodes/static/src/img/form_add_product_reset.png)

- If a scanned lot does not exist on a receipt, it can be created on the
  fly (*Create lots if not match*) or through the new lot dialog.
- Unknown packagings can be registered from the scan screen with the new
  packaging dialog: scan the packaging barcode, set the name and
  confirm.

## Barcode interface for inventory adjustments

Open *Barcodes > Inventory* (or the *Scan barcodes* button of an
inventory adjustment).

![Inventory barcode action](/stock_barcodes/static/src/img/inventory_barcode_action.png)

Scan a location, then products/lots/packages:

- Each product scan adds 1 unit to the counted quantity (or the
  packaging quantity when a packaging is scanned). With *accumulate read
  quantity* disabled, a new scan overwrites the counted quantity.
- Serial-tracked products accept exactly one unit per serial; a second
  read of the same serial is rejected.
- The eye icon switches between the items already counted by you and the
  pending ones.

  ![List items](/stock_barcodes/static/src/img/list_items.png)

- Each line in the list can be edited (pencil), incremented/decremented
  (+/-) or cleared (trash).

  ![List action items](/stock_barcodes/static/src/img/list_action_items.png)

- The *Apply* button is displayed when there are counted items. It opens
  the standard inventory adjustment confirmation (with reason), applies
  your counted quants and returns to the main menu.

  ![Apply inventory](/stock_barcodes/static/src/img/apply_inventory.png)

  ![Apply inventory reason](/stock_barcodes/static/src/img/apply_inventory_reason.png)

## Barcode actions

1. Go to *Barcodes*.
2. Scan an action barcode (see Configuration) to open the corresponding
   action directly, or tap its tile.

## Show the planned destination location on pending moves

By default the pending moves list on the barcode screen shows the source
location and lot of each move. When the option group has *Show fixed
dest. location* enabled, the list also shows the **destination location
already planned on the stock move line**, so the operator sees where the
goods must be stored as soon as the picking is opened, without scanning
anything.

This only **reads** the destination resolved upstream when the move was
prepared (e.g. the putaway strategy applied at reception). It never
recomputes the putaway: putaway is a warehouse decision taken when the
move is created, not a barcode-screen concern (see *Use location dest.
putaway* for the opposite, recompute-on-scan behaviour).

In addition, with this option enabled, **scanning a product reuses the
move line already routed by putaway** and keeps its destination, instead
of creating a new line at the generic picking destination. This way
receiving by barcode keeps the goods on their planned putaway location.

To keep the shown value reliable it is displayed only for moves whose
destination has **no storage category**, i.e. a fixed putaway whose
location does not depend on the received quantity. For capacity-based
putaway (storage categories) the final location may still change on a
partial receipt, so it is intentionally not shown.

Enable it in *Inventory > Configuration > Barcode Option Groups*, on the
option group used by the operation type, with the *Show fixed dest.
location* checkbox.
