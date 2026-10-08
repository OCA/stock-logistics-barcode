## Barcodes on master data

The interface recognizes four kinds of barcodes. Assign them first:

### Warehouse locations

1. You need the permission *Manage Multiple Stock Locations* to see the
   menu.

   ![Warehouse location access](/stock_barcodes/static/src/img/access_menu_warehouse_location.png)

2. Go to *Inventory > Configuration > Locations*.
3. Select the location and fill in the *Barcode* field.

   ![Warehouse location barcode](/stock_barcodes/static/src/img/barcode_warehouse_location.png)

### Product packagings

1. You need the permission *Manage Product Packaging* to see the menu.

   ![Product packaging access](/stock_barcodes/static/src/img/access_menu_product_packaging.png)

2. Go to *Inventory > Configuration > Product Packagings*.
3. Create or select a packaging and fill in the *Barcode* field.
   Scanning a packaging selects its product and proposes the packaging
   quantity.

   ![Product packaging barcode](/stock_barcodes/static/src/img/barcode_product_packaging.png)

### Products

1. Go to *Inventory > Products > Products*.
2. Fill in the *Barcode* field of each product.

### Lots / serial numbers

The lot **name** acts as its barcode, so no extra configuration is
needed (requires *Lots & Serial Numbers* enabled).

![Product lot barcode](/stock_barcodes/static/src/img/barcode_product_lot.png)

Packages are matched by their name, so scanning a package label selects
the package content (requires *Packages* enabled).

## Barcode option groups

Go to *Inventory > Configuration > Barcodes > Barcode Option Groups* to
define how the scan screen behaves. The first task of an implementation
is to analyze with the customer the flow of each operation (what is
labelled, what the operator reads and in which order, whether readings
are confirmed one by one) and adjust the options below to it. The
module ships six example groups: **Picking IN**, **Picking OUT**,
**Picking Internal**, **Relocation**, **Inventory** and a generic
**Operation** fallback. The **Inventory** group is always the one used
by the inventory scan screen.

### Steps to scan

GS1-128 labels (`stock_barcodes_gs1`) are decoded as a whole: the
product, lot and quantity they carry are set regardless of the steps.

The *Steps to scan* list defines, per field of the screen (location,
product, packaging, lot, package, destination, destination package,
quantity, owner, ...):

- **Step**: order in which the fields are asked. The current step is the
  step of the first required field still empty, and only the fields to
  scan of that step are matched against a barcode.
- **To scan**: the field can be filled by reading a barcode.
- **Required**: a reading is not processed while the field is empty.
- **Filled default**: the field is filled from the pending move (guided
  mode) or from the picking or operation type when the screen opens.
- **Forced** (guided mode): a value different from the pending move is
  rejected (*Wrong product*, *Wrong lot*, *Wrong location*).
- **Clean after done**: the field is emptied after each processed
  reading.

A field that is required but not scannable in its step can only be
filled by default, from the stock of a scanned lot or package, or by
hand in manual entry.

### Screen and confirmation

- **Mode**: *Guided* proposes one pending move at a time; empty means
  free mode, where barcodes are read in any order.
- **Manual entry**: open the screen with editable fields; **Manual entry
  on edit** switches to it when a pending move is edited with the pencil;
  **Manual entry field focus** is the field focused when switching.
- **Is manual confirm**: scans only fill the screen and the operator
  confirms each reading. Otherwise a reading is processed as soon as the
  required fields are filled.
- **Is manual qty**: the operator always types the quantity; scans do
  not set it.
- **Ignore filled fields**: a barcode skips the required fields that
  already have a value, e.g. so that a second location barcode sets the
  destination.
- **Keep screen values**: keep the values of the screen until the
  pending move is completed.
- **Show form scan**: keep the scan fields always visible; otherwise
  they are only shown in manual entry.
- **Show stock** and **Show owner**: show the quantity available in the
  location and the owner field on the screen.
- **Display Odoo notifications**: also notify when a reading is missing a
  required field.

### Pending moves

- **Show pending moves**: none, only pending or all (pending and done),
  built from the **operations** or the **detailed operations**
  (*Source pending moves*).
- **Group key for todo records**: expression grouping the pending moves,
  e.g. `object.picking_id,object.product_id`.
- **Location field to sort**: sort by source or destination location
  (X, Y, Z position and name). By default the destination is used for
  receipts and internal transfers and the source for the rest.
- **Show detailed operations**: show the detailed operations already
  read on the screen.
- **Confirmed moves**: also work on moves without reservation.

### Quantities

- **Replace quantity on each reading**: a confirmed reading replaces the
  quantity already recorded (done quantity of the detailed operation,
  counted quantity of the inventory) instead of being added to it.
  Editing a counted inventory line from the list always replaces it.
- **Accumulate repeated readings**: with manual confirmation, reading the
  same product, lot or packaging again before confirming adds one unit
  (or packaging) to the quantity to confirm. Combined with the previous
  option, units can be counted one by one on the screen and the result
  replaces the counted quantity.
- **Allow not demanded product**: accept products outside the picking
  demand, adding a move for them.
- **Allow negative quant**: accept quantities over the stock available in
  the location, and lots without stock.

### Lots, packages and locations

- **Fill fields from lot**: reading a lot or product fills product, lot,
  package, owner and location from its stock (not on receipts).
- **Ignore quant location**: when filling from stock, keep the location
  of the screen.
- **Get lots automatically** (pickings): propose the reserved lot, or the
  first one by removal strategy (not on receipts).
- **Create lots if not match**: accept new lot names; the lot is created
  with the reading in inventories and on validation in transfers.
- **Auto put in pack**: on validation of a picking of an operation type
  using the group, put its lines in a new package if none has one.
- **Use location dest. putaway**: when the destination is required and
  empty, compute it from the putaway strategy.
- **Show fixed dest. location**: show on each pending move the
  destination already planned by a fixed putaway, and make scans reuse
  that move line (see Usage).

### Other

- **Search picking from product**: when the screen is opened from an
  operation type, reading a product opens the first or last ready
  picking containing it.
- **Read items on inventory mode**: open the inventory screen listing
  the items already counted instead of the pending ones.
- **Code**: some codes change the behavior. *IN* does not take the
  source location from the stock of a scanned lot or package, *OUT* does
  not propose its quantity in stock, and *REL* accepts quantities over
  the demand without asking.

## Operation types

On each operation type (*Inventory > Configuration > Operation Types*)
you can select:

- **Barcode option group**: used when scanning the operation type or its
  pickings.
- **New picking barcode option group**: used when creating an unplanned
  picking from the barcode interface (*New* button).

The *Barcodes* tiles and the scanner button of the *Inventory > Overview*
cards only list operation types with a barcode option group. The *Scan
barcodes* button of a transfer uses the generic *Operation* group when
its operation type has none.

## Barcode actions

*Inventory > Configuration > Barcodes > Barcode Actions* define the
tiles shown in the *Barcodes* main menu. Each action can have its own
barcode: scanning it from the main menu opens the action directly.

![Create barcode action](/stock_barcodes/static/src/img/create_barcode_action.png)

Select actions and press *Print barcodes* to generate a PDF with their
Code128 barcodes, e.g. for a laminated menu sheet.

![Print barcodes](/stock_barcodes/static/src/img/print_barcodes.png)

## System parameters

The system parameter `stock_barcodes.limit_product_qty` (default
999999) rejects absurd quantities caused by scanning a barcode into a
quantity input.
