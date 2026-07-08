## 18.0.1.3.0 (2026-07-08)

- \[FIX\] Restore bus notifications broken by the 18.0 bus API: scanning
  an action barcode from the main menu, the "transfer validated" toast
  and the manual-edit toggle from a pending line. Events are now sent to
  the scanning user only instead of a broadcast channel.
- \[FIX\] Notify only the most significant message per interaction.
  Reading a barcode triggers sequential lookups and checks that buffer
  intermediate messages (e.g. "Manual entry OK" before the availability
  check rejects the entry), and each one used to raise its own
  notification. Messages are now buffered on the wizard (last one wins,
  as the on-screen message field always behaved) and a single
  notification is sent when the read or the manual confirmation ends:
  always for errors, only in manual entry for informative messages, and
  for "Manual entry OK" only when the whole confirmation succeeded.
- \[FIX\] Show each barcode notification only once. The barcode views
  subscribed the same handler to two bus notification types, which leaks
  a listener on every render (the bus service maps subscriptions by
  callback), so each notification was displayed more and more times as
  the session went on.
- \[FIX\] Barcode action tile counters: the model-field check never
  matched (checked attributes on a string), so tiles counted all records
  of the model; named filters now count records matching the filter.
- \[REF\] Remove pre-17.0 immediate-transfer leftovers, use
  `_read_group` aggregation, convert the report model to
  `AbstractModel`, drop a duplicated ACL, replace deprecated `t-esc`
  with `t-out` and add `limit=1` to singleton barcode lookups.
- \[REF\] Rename misspelled methods (`_set_message_info`,
  `check_location_condition`, `check_lot_condition`). The old names are
  kept as deprecated aliases; modules overriding them must move their
  override to the new names.

## 18.0.1.1.0 (2026-06-22)

- \[ADD\] New option *Show fixed dest. location* on barcode option groups.
  It shows, in the pending moves list, the destination location already
  planned on the stock move line (for a fixed putaway, destination without
  storage category), and makes a scan reuse that move line keeping its
  destination instead of duplicating it at the generic picking destination.
  It never recomputes the putaway strategy.

## 11.0.1.1.0 (2019-09-24)

- \[ADD\] New feature. User can uses barcode interface in picking
  operations.

## 13.0.1.1.1 (2021-02-06)

- \[ADD\] New feature. Add option to get lots automatically based on
  removal strategy in inventory.

## 14.0.1.0.0 (2021-04-05)

- \[ADD\] New feature. Add security for users.

## 16.0.1.0.0 (2025-01-23)

- \[IMP\] Improved views to optimize navigation and functionality.
  Intuitive and mobile-friendly views. Visual improvement of the main
  view accessed from the Barcodes menu.
- \[ADD\] New feature. Barcode reading to barcode actions. Generate PDF
  document for the barcodes of the selected barcode actions.
