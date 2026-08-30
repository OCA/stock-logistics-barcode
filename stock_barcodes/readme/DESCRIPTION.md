This module provides a barcode scanning interface for stock operations:
receipts, deliveries, internal transfers, relocations and inventory
adjustments.

It is designed for keyboard-wedge scanners (USB/Bluetooth) and works on
desktop and mobile browsers, without requiring the Odoo Enterprise
barcode application.

Main features:

- A scan screen for pickings and operation types, in **free** or
  **guided** mode (the screen proposes one pending move at a time and
  validates what the operator scans).
- A scan screen for **inventory adjustments** writing counted quantities
  on stock quants.
- Recognition of product, product packaging, lot/serial, package and
  location barcodes.
- **Barcode option groups**: a data-driven configuration of the screen
  behavior per operation type (fields to scan, required, pre-filled,
  forced, cleaned after each read, steps, backorder handling, putaway
  handling, etc.).
- A **Barcodes** main menu with configurable, printable barcode actions
  (scan an action barcode to open it).
- A base abstract wizard (`wiz.stock.barcodes.read`) that other modules
  extend (GS1, batch picking, ...).
