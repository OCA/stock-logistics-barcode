# Stock Barcodes — User Guide

This guide explains how to configure and use the barcode scanning interface provided by
the `stock_barcodes` module for warehouse operations: receipts, deliveries, internal
transfers, relocations and inventory adjustments.

The interface is designed for keyboard-wedge scanners (USB/Bluetooth scanners that type
the barcode followed by Enter) and works on desktop and mobile browsers. No Odoo
Enterprise barcode license is required.

## 1. Configuration

### 1.1 Barcodes on master data

The interface can recognize four kinds of barcodes. Assign them first:

- **Products** — _Inventory > Products > Products_, field _Barcode_.
- **Warehouse locations** — _Inventory > Configuration > Locations_, field _Barcode_
  (requires the _Manage Multiple Stock Locations_ permission to see the menu).
- **Product packagings** — _Inventory > Configuration > Product Packagings_, field
  _Barcode_ (requires _Manage Product Packaging_). Scanning a packaging selects its
  product and proposes the packaging quantity.
- **Lots / serial numbers** — the lot **name** acts as its barcode, no extra
  configuration is needed (requires _Lots & Serial Numbers_ enabled).

Packages (`stock.quant.package`) are matched by their name, so scanning a package label
selects the package content (requires _Packages_ enabled).

### 1.2 Option groups

_Inventory > Configuration > Barcodes > Barcode Option Groups_ define how the scan
screen behaves. The module ships six ready-to-use groups: **Picking IN**, **Picking
OUT**, **Picking Internal**, **Relocation**, **Inventory** and a generic **Operation**
fallback.

For each group you can configure, among others:

- **Mode — Guided**: the screen proposes one pending move at a time and validates that
  the operator scans the expected product/lot/location. Without guided mode the operator
  scans freely against the picking.
- **Options list**: per field (product, lot, package, source location, destination,
  quantity, …) whether it must be _scanned_, is _required_, comes _pre-filled_, is
  _forced_ (guided mode rejects a different value) and whether it is _cleaned after each
  confirmation_. Fields are grouped in _steps_: the screen tells the operator what to
  scan next.
- **Manual entry / manual confirmation / manual quantities**: show editable fields and
  require pressing _Confirm_ instead of confirming on each scan.
- **Show pending moves**: display the list of moves to process (only pending, or all
  including done).
- **Confirmed moves**: allow working on moves without stock reservation.
- **Get lots automatically**: pick the lot using the product removal strategy
  (FIFO/FEFO) instead of scanning it.
- **Create lots if not match**: on receipts, scanning an unknown lot creates it on the
  fly.
- **Allow negative stock**, **accumulate read quantity**, **auto put in pack**, **keep
  screen values**, and other fine-tuning flags (each field has an explanatory tooltip).
- **Use location dest. putaway**: when the destination is required and empty, compute it
  from the putaway strategy.
- **Show fixed dest. location**: show on each pending move the destination already
  planned by a fixed putaway, and make scans reuse that move line (see section 5).

### 1.3 Operation types

On each operation type (_Inventory > Configuration > Operation Types_) you can select:

- **Barcode option group**: the group used when scanning this operation type or its
  pickings.
- **New picking barcode option group**: the group used when creating an unplanned
  picking from the barcode interface (_New_ button).

If no group is set, the generic _Operation_ group is used.

### 1.4 Barcode actions

_Inventory > Configuration > Barcodes > Barcode Actions_ define the tiles shown in the
_Barcodes_ main menu (Receipts, Delivery, Internal, Inventory, …). Each action can have
its own **barcode**: scanning it from the main menu opens the action directly — useful
for laminated menu sheets. Select actions and press **Print barcodes** to generate a PDF
with their Code128 barcodes.

## 2. Scanning pickings

You can open the scan screen from three places:

1. **Barcodes main menu** (app _Barcodes_): choose an operation tile, then pick one of
   the ready transfers from the list.
2. **An operation type card** in _Inventory > Overview_ (scanner button): scan products
   for any ready picking of that type.
3. **A specific transfer** (_Scan barcodes_ button): the picking is locked and every
   scan applies to it.

### 2.1 Free mode

Scan in any order; the screen reacts to the kind of barcode read:

- **Product**: adds 1 unit (or waits for a lot if the product is tracked). The source
  location is resolved automatically from the pending reserved lines.
- **Packaging**: selects the product and adds the packaging quantity.
- **Lot**: requires the product first when several lots share the name; when _fill
  fields from lot_ is active, scanning a lot fills product, package, owner and location
  from the available stock.
- **Package**: fills all fields from the package content.
- **Location**: sets the source (or destination, per configuration) for the following
  scans.

Quantities beyond the picking demand or beyond available stock are not written silently:
the screen asks for confirmation (_force done_) or rejects the scan, depending on the
option group.

### 2.2 Guided mode

The screen shows the next pending move (product, lot, quantities, locations) and guides
the operator step by step (e.g. _Scan Source_, then _Scan Product, Lot_). Scanning
something different from what is expected is rejected with an explicit message (_Wrong
product_, _Wrong lot_, _Wrong location_). The pending-moves list allows to:

- jump to another line (arrows or tapping a card),
- put the whole remaining quantity with the **+N** button,
- reset a processed line (trash icon) or edit it (pencil icon),
- decide the backorder behavior per line when quantities are incomplete (create
  backorder / no backorder / keep pending).

### 2.3 Validation

The **Validate** button confirms the transfer using the scanned quantities. If some
lines have no quantity, the standard confirmation wizards are shown. After validation
you return to the ready-pickings list. With _Auto put in pack_ enabled, unpacked lines
are packed automatically before validating.

### 2.4 Extra products, new lots and packagings

- **+ Product** opens a manual form to add an item not in the demand (when the option
  group allows non-demanded products).
- If a scanned lot does not exist on a receipt, it can be created on the fly (_Create
  lots if not match_) or through the **new lot** dialog.
- Unknown packagings can be registered from the scan screen with the **new packaging**
  dialog: scan the packaging barcode, set the name and confirm.

## 3. Inventory adjustments

Open _Barcodes > Inventory_ (or the _Scan barcodes_ button of an inventory adjustment).
Scan a location, then products/lots/packages:

- Each product scan adds 1 unit to the counted quantity (or the packaging quantity when
  a packaging is scanned). With _accumulate read quantity_ disabled, a new scan
  overwrites the counted quantity instead.
- Serial-tracked products accept exactly one unit per serial; a second read of the same
  serial is rejected.
- The **eye** button switches between the items already counted by you and the pending
  ones; the counter shows how many quants you have counted.
- Each line in the list can be edited (pencil), incremented/decremented (+/-) or cleared
  (trash).
- **Apply** opens the standard inventory adjustment confirmation (with reason), applies
  your counted quants and returns to the main menu.

## 4. Screen feedback

- A **bell** sound confirms a successful scan; an **error** sound signals a rejected
  one.
- Status messages under the barcode field explain what the screen is waiting for (_Scan
  Product, Lot_, _Waiting quantities_, …) and why a scan was rejected.
- Odoo toast notifications can be enabled per option group (_Display Odoo
  notifications_).
- The **Manual** button toggles manual entry to type values without a scanner; quantity
  fields use +/- steppers sized for touch screens.

## 5. Putaway destinations on pending moves

With **Show fixed dest. location** enabled on the option group, the pending-moves list
also shows the destination location already planned on each move line, so the operator
knows where goods must be stored before scanning. The value is shown only for _fixed_
putaways (destinations without storage category), whose location does not depend on the
received quantity. Scanning a product then reuses the move line routed by putaway and
keeps its planned destination instead of creating a duplicate line at the generic
picking destination. The putaway strategy is never recomputed on the barcode screen —
use _Use location dest. putaway_ for the opposite, recompute-on-scan behavior.

## 6. Tips

- The quantity guard system parameter `stock_barcodes.limit_product_qty`
  (default 999999) rejects absurd quantities caused by scanning a barcode into a
  quantity input.
- Scan-screen sessions survive navigation: reopening the picking or menu returns to the
  same wizard for up to 48 hours.
- All behavior differences between receipt/delivery/internal/inventory screens come from
  the option groups — duplicate a shipped group and adjust it rather than starting from
  scratch.
