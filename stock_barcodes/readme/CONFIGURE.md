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
define how the scan screen behaves. The module ships six ready-to-use
groups: **Picking IN**, **Picking OUT**, **Picking Internal**,
**Relocation**, **Inventory** and a generic **Operation** fallback.

For each group you can configure, among others:

- **Mode — Guided**: the screen proposes one pending move at a time and
  validates that the operator scans the expected product/lot/location.
- **Options list**: per field (product, lot, package, locations,
  quantity, ...) whether it must be scanned, is required, comes
  pre-filled, is forced and whether it is cleaned after each
  confirmation. Fields are grouped in *steps*: the screen tells the
  operator what to scan next.
- Manual entry / manual confirmation / manual quantities.
- **Show pending moves** (only pending, or all) and their data source
  (operations or detailed operations).
- **Confirmed moves**: allow working on moves without reservation.
- **Get lots automatically** (removal strategy) and **Create lots if
  not match** (receipts).
- Allow negative stock, accumulate read quantity, auto put in pack,
  keep screen values, and other fine-tuning flags (each field has an
  explanatory tooltip).
- **Use location dest. putaway**: when the destination is required and
  empty, compute it from the putaway strategy.
- **Show fixed dest. location**: show on each pending move the
  destination already planned by a fixed putaway, and make scans reuse
  that move line (see Usage).

## Operation types

On each operation type (*Inventory > Configuration > Operation Types*)
you can select:

- **Barcode option group**: used when scanning the operation type or its
  pickings.
- **New picking barcode option group**: used when creating an unplanned
  picking from the barcode interface (*New* button).

If no group is set, the generic *Operation* group is used.

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
