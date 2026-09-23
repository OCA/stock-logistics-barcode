The barcode interface is driven entirely by data, not by code: an *option
group* describes which fields the interface asks for, in which order, and how
it behaves while scanning. Nothing needs to be configured to try the module
out — six option groups are installed as demo-free default data — but any real
deployment will want to review them.

Where the configuration lives
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#. Go to *Inventory > Configuration > Barcode options* to create or edit
   option groups.
#. Go to *Inventory > Configuration > Operation Types*, open an operation type
   and set:

   * **Barcode option group**: the option group used when the barcode
     interface is opened for that operation type or for one of its transfers.
     The *Scan barcodes* button only appears once this field is set.
   * **New picking barcode option group**: the option group used by the *New*
     button of the operation type, to create an unplanned picking.

#. Locations need a barcode to be scannable. The *Barcode* field was removed
   from the location form in Odoo 13.0, so this module adds it back under
   *Inventory > Configuration > Locations*, in the *Barcode* group.

Option groups delivered by default
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

============================= ==== ==============================================
Name                          Code Intended use
============================= ==== ==============================================
Picking IN options            IN   Receipts
Picking OUT options           OUT  Deliveries (guided mode, manual qty)
Picking Internal options      INT  Internal transfers
Picking relocation options    REL  Moving stock between locations
Inventory options             INV  Inventory adjustments
Operation options             OPE  Entry point of the *Operations* menu
============================= ==== ==============================================

These records are created with ``noupdate="1"``, so your changes to them are
kept across module updates. Copying a group (the ``option_ids`` lines are
copied too) is usually safer than editing a default one.

Steps to scan
~~~~~~~~~~~~~

The *Steps to scan* list of an option group is the core of the configuration.
Each line binds one field of the scan wizard to the scanning workflow:

* **Field name** is the technical name of the wizard field the line refers to
  (``product_id``, ``lot_id``, ``location_id``, ``location_dest_id``,
  ``package_id``, ``result_package_id``, ``packaging_id``, ``product_qty``,
  ``packaging_qty``, ``owner_id``). A scanned barcode is resolved by calling
  ``process_barcode_<field name>`` on the wizard, so a line whose field name
  has no such method will never match a barcode.
* **Step** groups lines into successive screens. The interface is always
  positioned on one step, and only the lines of the current step are candidates
  for the barcode being scanned. The current step is recomputed after each scan:
  it becomes the step of the first *required* line that is still empty.
* **Sequence** orders the lines inside a step. The interface tries them in that
  order and stops at the first one that resolves the barcode, so put the most
  specific field first — for example a package before a product, since a
  package barcode would otherwise never be reached.
* **To scan** makes the line a candidate for barcode resolution. Lines that are
  not *to scan* can still be filled manually or by another line's side effects,
  but scanning will never assign them. The names of the *to scan* lines of the
  current step are what the interface displays as *Scan ...*.
* **Required** prevents the movement from being processed while the field is
  empty, and is what drives step navigation. ``lot_id`` is skipped when the
  product is not tracked, or when *Get lots automatically* or *Create lots if
  not match* apply.
* **Filled default** pre-fills the field with the value of the movement to
  process each time the interface presents a new one, instead of emptying it.
  When the interface is opened from an operation type or a transfer, the
  locations are pre-filled with its default ones, and in inventory mode the
  source location comes from the stock location of the first warehouse. For
  ``product_qty`` it also disables the automatic "1 unit per scan" increment,
  leaving the quantity to the user.
* **Forced** makes the value already set in the field prevail. On
  ``location_id`` it keeps the location entered by the user instead of taking
  the one of a scanned lot or package, restricts the search for a package to
  it, and forbids reusing an existing detailed operation that has a different
  location, so a new one is created instead. In guided mode it additionally
  rejects a scan whose product, lot or location does not match the movement
  being guided (*Wrong product*, *Wrong lot*, *Wrong location*).
* **Clean after done** empties the field once the movement is confirmed. Leave
  it unchecked for fields that should persist between scans, typically the
  source location.

As an example, the *Picking OUT options* group is configured as three steps:
package, product and lot in step 1, the source location in step 2 (pre-filled
and forced) and the quantity in step 3.

Behavior settings
~~~~~~~~~~~~~~~~~

The remaining fields of the option group form change how the interface
behaves. They are documented in the tooltip of each field; the ones worth
knowing before a first configuration are:

* **Mode**: set it to *Guided* to display the movement that has to be
  processed and to enable the *Forced* option of the steps.
* **Manual entry**: opens the interface with manual entry already enabled, so
  values can be typed instead of scanned. The hardware scanner stays active.
  **Field to focus on manual entry** decides which field gets the focus then.
* **Show pending moves** / **Source of pending moves**: display the list of
  movements left to process, taken either from the detailed operations
  (``move_line_ids``) or from the operations (``move_ids``). Choose
  ``move_ids`` together with **Confirmed moves** to work without reservations.
* **Ignore filled fields**: skip the required fields that already have a value
  when resolving a barcode, instead of trying to overwrite them.
* **Group key for todo records**: an expression list used to group the source
  records into the movements to process, for example
  ``object.location_id,object.product_id,object.lot_id``.
* **Accumulate read quantity**: add the scanned quantity to the existing line
  instead of replacing it — usually what is expected when the same product is
  scanned several times.

Barcode actions
~~~~~~~~~~~~~~~

Barcode actions are the tiles of the *Barcodes* menu, and they can be reached
by scanning a barcode instead of touching the screen. Go to
*Inventory > Configuration > Barcode Actions* to configure them:

* **Action window** is the window action to execute, and **Context** an
  optional context added to it, for instance
  ``{'search_default_code': 'incoming'}`` to open the action with a filter of
  its search view already applied. The context must not start or end with a
  space.
* **Barcode** is the barcode that triggers the action. Letters, digits and
  dashes only, no spaces, and it must be unique across actions. A printable
  barcode image is generated from it.
* **Key char shortcut** has no effect: the kanban template of the menu reads
  it but never displays it nor binds it to a key handler, and the shortcuts of
  the interface (F2, F4, F9, F12) are hard coded. **Icon class** is the CSS
  class of the icon of the tile, typically a Font Awesome one.

Select the actions you want and use the *Print barcodes* button to get a PDF
of their barcodes, ready to be posted next to the workstation.
