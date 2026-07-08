# Stock Barcodes — Technical Documentation

Module: `stock_barcodes` (18.0.1.3.0) — OCA `stock-logistics-barcode`

This document describes the internal architecture of the module, its extension points,
and the result of the Odoo 18.0 alignment review.

## 1. Purpose and architecture

`stock_barcodes` provides a keyboard-wedge barcode scanning interface for stock
operations, built on top of the standard `barcodes` addon (community). It does not
depend on the Enterprise `stock_barcode` module.

The architecture has three layers:

1. **Scan wizards** (`TransientModel`): a reusable abstract wizard
   (`wiz.stock.barcodes.read`) plus concrete wizards for picking operations
   (`wiz.stock.barcodes.read.picking`) and inventory adjustments
   (`wiz.stock.barcodes.read.inventory`). Wizard records are kept alive for 48 hours
   (`_transient_max_hours = 48`) so an operator session survives navigation and vacuum.
2. **A data-driven option engine** (`stock.barcodes.option.group` /
   `stock.barcodes.option`): each operation type is bound to an _option group_ that
   declares, per wizard field, whether it must be scanned, is required, is pre-filled,
   is forced (guided mode) and/or is cleaned after each confirmation. Behavior is
   configuration, not code.
3. **An OWL frontend** (ESM components under `static/src`): a barcode main menu client
   action, a form controller/renderer that keeps a hidden barcode handler focused,
   kanban components for the pending-moves cards and real-time updates through
   `bus.bus`.

### Models

| Model                               | Type           | Role                                                                                            |
| ----------------------------------- | -------------- | ----------------------------------------------------------------------------------------------- |
| `wiz.stock.barcodes.read`           | AbstractModel  | Base scan wizard: barcode routing, messages, sounds, steps                                      |
| `wiz.stock.barcodes.read.picking`   | TransientModel | Scanning against pickings / operation types                                                     |
| `wiz.stock.barcodes.read.inventory` | TransientModel | Scanning for inventory adjustments (writes `stock.quant.inventory_quantity`)                    |
| `wiz.stock.barcodes.read.todo`      | TransientModel | "Pending moves" cards: grouped view of moves/move lines to process                              |
| `wiz.stock.barcodes.new.lot`        | TransientModel | Create/select a lot from the scan screen                                                        |
| `wiz.stock.barcodes.new.packaging`  | TransientModel | Create/select a product packaging from the scan screen                                          |
| `stock.barcodes.option.group`       | Model          | Behavior profile bound to an operation type                                                     |
| `stock.barcodes.option`             | Model          | Per-field behavior (to_scan, required, forced, filled_default, clean_after_done, step)          |
| `stock.barcodes.action`             | Model          | Barcode-triggered window actions (main menu), printable Code128 image                           |
| `stock.move` (inherit)              | —              | `barcode_backorder_action`, `qty_picked` (computed sum), backorder handling in `_action_done()` |
| `stock.move.line` (inherit)         | —              | `barcode_scan_state`, `qty_picked` (scanned quantity, decoupled from reservation)               |
| `stock.picking` (inherit)           | —              | Wizard bootstrap (`action_barcode_scan`), `button_validate()` integration                       |
| `stock.picking.type` (inherit)      | —              | Option group binding, scan from operation type, unplanned picking                               |
| `stock.quant` (inherit)             | —              | Inventory-mode kanban actions (+1/-1, edit, clear), owner edit whitelist                        |

### Key design decision: `qty_picked`

Since Odoo 17 the core replaced `stock.move.line.qty_done` with `quantity` + `picked`.
The module keeps its own `qty_picked` float on `stock.move.line`, decoupled from the
reserved `quantity`, so scanning can accumulate partial quantities without touching the
reservation. On validation from the barcode interface,
`stock.picking.set_quantity_from_picked()` copies `qty_picked` into `quantity` before
calling the standard `button_validate()`. The compute `_compute_qty_picked` seeds
`qty_picked` from `quantity` when the line is `picked` or done (store=True,
readonly=False: an editable compute used as a smart default).

`barcode_scan_state` (`pending` / `done` / `done_forced`) tracks scanning progress per
move line and drives the pending-moves cards.

## 2. Scan processing pipeline

Entry point: `on_barcode_scanned(barcode)` (from `barcodes.barcode_events_mixin`) stores
the barcode; `dummy_on_barcode_scanned()` is then invoked by the client outside the
onchange environment and calls `process_barcode(barcode)`:

1. The option group's options with `to_scan` and matching current `step` are iterated in
   order; for each one the wizard calls `process_barcode_<field_name>()` (e.g.
   `process_barcode_product_id`, `process_barcode_lot_id`, `process_barcode_package_id`,
   `process_barcode_location_id`, `process_barcode_packaging_id`,
   `process_barcode_result_package_id`, `process_barcode_lot_name`). The first handler
   returning `True` wins. Adding support for a new scannable field only requires an
   option row plus a `process_barcode_<field>` method.
2. `check_option_required()` verifies every `required` option is filled (with
   lot/auto-lot/putaway hooks — see `_option_required_hook`).
3. Unless manual confirmation is configured, `action_confirm()` runs: it persists the
   onchange cache, then calls `action_done()`.
4. `action_done()` validates quantities (`stock_barcodes.limit_product_qty` config
   parameter guards against a barcode scanned into a qty input), runs
   `check_done_conditions()` (+ guided-mode checks `_check_guided_values`), then the
   concrete wizard applies the result:
   - picking wizard: `_process_stock_move_line()` distributes the scanned quantity over
     candidate move lines, creating extra lines/moves when demand is exceeded
     (`force_create_move`);
   - inventory wizard: `_add_inventory_quant()` writes `inventory_quantity` on the
     matching quant (create in `inventory_mode`), with serial-tracking guards and
     optional accumulation (`accumulate_read_quantity`).
5. Feedback: sounds (`play_sounds`), sticky/transient notifications and focus control
   are pushed to the client over `bus.bus` (`send_bus_done()` sends to the current
   user's partner channel).

### Candidate move line resolution (picking wizard)

`_process_stock_move_line()` is the heart of the picking flow:

- Moves considered: the guided todo line's moves, the picking's moves, or a `stock.move`
  search by product/operation-type/state (`_states_move_allowed()` adds `confirmed` when
  the group allows working without reservation).
- `_get_candidate_stock_move_lines()` matches lines by source/destination location and
  product, with fallbacks that relocate the line's source or destination when the
  corresponding option is not `forced` (a scanned bin wins over the planned one), and a
  putaway-aware fallback (`show_fixed_location_dest`) that reuses the line already
  routed by putaway instead of duplicating it at the generic picking destination.
- Serial numbers are deduplicated against the picking (`S/N Already in picking`), lots
  are propagated to reception lines without a lot, and quantities beyond demand raise
  the _force done_ confirmation instead of writing silently.
- Excess quantity creates extra `stock.move.line` records (`_prepare_move_line_values`,
  `barcode_scan_state = "done_forced"`) and, when there is no move to attach to, an
  `additional` `stock.move` (`create_new_stock_move`).

### Pending moves ("todo" records)

`fill_records()` groups moves or move lines (per `source_pending_moves`: `move_ids` vs
`move_line_ids`) by `_group_key()` — overridable through the option group's
`group_key_for_todo_records`, a `safe_eval` expression over `object`. Each group becomes
a `wiz.stock.barcodes.read.todo` card with reserved/demand/done quantities, navigation
(`action_back_line` / `action_next_line`), reset (`action_reset_lines`) and "process
remaining" (`operation_quantities`, `action_todo_next` with per-move
`barcode_backorder_action`). In guided mode `determine_todo_action()` selects the next
pending card and fills guided/default values according to the options.

### Backorder handling

`stock.move.barcode_backorder_action` (`pending` / `create_backorder` /
`skip_backorder`) is set per move from the todo cards. `stock.move._action_done()`
splits the recordset so that moves flagged `skip_backorder` are validated with
`cancel_backorder=True`, and it is excluded from `copy_data()` so backorder moves
restart as `pending`.

## 3. Option groups

`stock.barcodes.option.group` centralizes behavior. The most relevant flags (see field
help strings for the full list): `barcode_guided_mode` (guided vs free), `manual_entry`,
`is_manual_qty`, `is_manual_confirm`, `confirmed_moves` (work without reservation),
`show_pending_moves` (`none`/`pending`/`all`), `source_pending_moves`, `auto_lot`
(removal strategy via `stock.quant._gather`), `create_lot`, `fill_fields_from_lot`,
`allow_negative_quant`, `accumulate_read_quantity`, `auto_put_in_pack`,
`use_location_dest_putaway` (recompute putaway with `_get_putaway_strategy()` when
destination is required and empty), `show_fixed_location_dest` (read — never recompute —
the putaway destination already planned on the move line), `keep_screen_values`,
`no_increase_qty_done`, `search_picking_from_product`, `allow_not_demanded_product`,
`show_detailed_operations`, `display_notification`, `show_stock`, `show_owner`.

Six option groups are shipped as `noupdate="1"` data: Picking OUT (`OUT`), Picking IN
(`IN`), Internal, Relocation (`REL`), Inventory and the generic fallback Operation group
(used when the picking type has no `barcode_option_group_id`).

`stock.picking.type` gets two Many2one fields: `barcode_option_group_id` (used when
scanning against the type or a picking) and `new_picking_barcode_option_group_id` (used
by _New_ to create an unplanned picking).

## 4. Frontend

All assets are ESM modules registered in `web.assets_backend` (ordered injection with
`("after", ...)` for inherited XML templates):

- `views/actions/stock_barcode_main_menu.esm.js`: client action
  (`stock_barcodes_main_menu` bus channel) that lists `stock.barcodes.action` records as
  tiles, listens for scanned action barcodes and executes the linked window action.
- `views/form/form_controller.esm.js` + `form_view.esm.js`: barcode form variant that
  hides the control panel, guards the optional `barcode` service and manages listener
  cleanup.
- `views/kanban/*`: kanban record/renderer used by the pending-moves and
  inventory-quants embedded lists (per-record actions such as +1/-1, edit, trash)
  reacting to `stock_barcodes_kanban_update` bus payloads.
- `utils/barcode_handler_field.esm.js` and `barcodes_models_utils.esm.js`: keep the
  invisible barcode input focused and route `stock_barcodes_scan` bus payloads (sounds
  via `bell.wav`/`error.wav`, notifications, manual-entry toggle, focus requests).
- `widgets/`: `numeric_step` (extends OCA `web_widget_numeric_step`), `boolean_toggle`,
  `view_button` template extension.

Bus channels: every payload goes through the current user's partner channel
(auto-subscribed by the websocket for authenticated sessions), either via
`send_bus_done()` → `_sendone(self.env.user.partner_id, notification_type, data)` or
direct `_sendone` calls with the partner as target. The client reacts with
`bus_service.subscribe(notification_type, cb)`; the main menu also calls
`bus_service.start()` because `subscribe()` alone does not start the bus connection.

## 5. Reports, hooks, security, packaging

- **Report**: `report.stock_barcodes.report_barcode_actions` renders a PDF with the
  Code128 images of the selected barcode actions. Images are generated with the external
  `python-barcode` library (`stock.barcodes.action._generate_barcode`).
- **pre_init_hook**: creates `stock_move_line.barcode_scan_state`,
  `stock_move_line.qty_picked` and `stock_move.barcode_backorder_action` by SQL before
  the ORM loads, and seeds `qty_picked = quantity`, so installation on a large database
  avoids the ORM per-record default.
- **Migrations**: `18.0.1.0.0` pre/post scripts (openupgradelib) create `qty_picked`
  from the removed `qty_done` and convert `show_pending_moves` from boolean to
  selection.
- **Security**: plain ACLs on the wizards and configuration models (`base.group_user`;
  `stock.barcodes.action` writable only by `base.group_system`). Feature gating reuses
  core groups (`stock.group_production_lot`, `stock.group_tracking_lot`,
  `product.group_stock_packaging`).
- **Packaging**: PEP 517 `pyproject.toml` (whool); external dependency `python-barcode`
  declared in the manifest.

## 6. Extension points

The module is designed to be inherited (e.g. `stock_barcodes_gs1`,
`stock_barcodes_picking_batch`):

- `process_barcode_<field_name>()` — add scannable fields.
- `_barcode_domain(barcode)` — barcode matching domain (`barcode_domain_field` context
  key).
- `_option_required_hook(option)` — bypass required options (used by
  `use_location_dest_putaway`).
- `process_lot_before_done()` — e.g. GS1 expiry handling.
- `_prepare_move_line_values()`, `_update_stock_move_line()`,
  `_get_candidate_line_domain()` — move line creation/matching.
- `_group_key()`, `_prepare_fill_record_values()`, `_update_fill_record_values()` —
  pending-cards grouping.
- `_get_location_domain_for_quant_search()` — quant lookup scope.
- `_states_move_allowed()`, `_prepare_stock_moves_domain()` — candidate moves.
- `_fill_fields_from_lot_active()` — disable stock prefill per flow (receptions return
  `False`).

## 7. Odoo 18.0 alignment review

### Confirmed aligned

- **`quantity`/`picked` paradigm**: no usage of the removed `stock.move.line.qty_done`;
  the module's own `qty_picked` + `set_quantity_from_picked()` before
  `button_validate()` is consistent with the 17/18 core.
- **Product typing**: `_allowed_product_types = ["consu"]` and the inventory wizard
  domain `[("is_storable", "=", True)]` match the 18.0 model (`type` ∈
  consu/service/combo + `is_storable` boolean).
- **`stock.lot`** used everywhere (renamed from `stock.production.lot` in 16.0).
- **`copy_data()`** overridden with the 17+ vals-list signature.
- **Views**: no `attrs`/`states` (removed in 17.0), `<list>` syntax, no deprecated view
  attributes.
- **Frontend**: OWL 2 ESM components, `useService`, bus `addChannel`/`addEventListener`
  subscription model, manifest asset ordering — all current 18.0 patterns.
- **ORM API**: `@api.model_create_multi`, `invalidate_recordset()`, `filtered_domain()`,
  `float_compare`/`float_round` with `precision_rounding`, `Command` in tests,
  `_for_xml_id()`.
- **`_get_putaway_strategy(product, quantity, package, packaging)`** matches the 18.0
  signature.
- **`pre_init_hook(env)`** uses the 17+ single-`env` signature.
- **Test suite**: 101 tests on `TransactionCase` with `mail_new_test_user`, covering
  picking (free/guided), inventory, lots, serial handling, option groups, reports and
  todo logic.

### Findings fixed in 18.0.1.3.0

1. **Dead immediate-transfer code** — `stock.picking.type. action_barcode_new_picking()`
   and `_get_action()` injected `default_immediate_transfer` and read the
   `stock.no_default_immediate_tranfer` (sic) parameter. The `immediate_transfer` field
   was removed from core in 17.0; the inert context keys were removed.
2. **Legacy `read_group`** — `_compute_qty_available` called
   `read_group(domain, ["quantity"], groupby=["id"])`; grouping by `id` defeats
   aggregation. Replaced with
   `self.env["stock.quant"]._read_group(domain, aggregates=["quantity:sum"])` (one
   aggregated query, current API).
3. **Broken bus notifications (v18 bus API)** — three `_sendone` calls targeted the
   string channel `stock_barcodes_scan`, which no client subscribes to as a _channel_
   (the frontend subscribes per _notification type_ on the implicit partner channel);
   the main-menu component additionally used the removed
   `addEventListener("notification")` API. As a result, the main-menu action-barcode
   scan, the "transfer validated" toast and the edit-manual toggle from a pending line
   were silently dead. All three now target `self.env.user.partner_id` with the envelope
   expected by the client, and the main menu uses `bus_service.subscribe()` + `start()`.
   As a bonus, events are now per-user, so multi-station deployments no longer risk
   cross-user notifications.
4. **Report model persistence** — `report.stock_barcodes.report_barcode_actions` was a
   `models.Model`; report value providers must be `models.AbstractModel` (no table, no
   ACL). Converted, and its ACL row dropped.
5. **Duplicate ACL** — `access_stock_barcodes_read_picking` duplicated
   `access_wiz_stock_barcodes_read_picking`; removed.
6. **Manifest hygiene** — redundant `base` dependency removed (`mail` is kept: the test
   suite imports `mail_new_test_user`).
7. **`t-esc` in kanban QWeb** (`stock_barcodes_read_todo_view.xml`) — replaced with
   `t-out`.
8. **`stock.barcodes.action._count_elements()`** — used
   `hasattr(self.action_window_id.res_model, field_name)` where `res_model` is a
   _string_, so the check never matched a model field and the tile counter silently
   counted **all** records of the model. Now it checks `self.env[res_model]._fields`;
   named filters mapped through `FIELDS_NAME` count records with the field set (matching
   the search filter domain), and an unresolvable `search_default_` key yields 0 instead
   of a meaningless total.
9. **API typos** — `_set_messagge_info`, `check_location_contidion` and
   `check_lot_contidion` were renamed to `_set_message_info`, `check_location_condition`
   and `check_lot_condition`. The misspelled names remain as deprecated delegating
   aliases for external callers; note that downstream modules _overriding_ the old names
   must move their override to the new names (internal calls now use them).
10. **Unbounded searches** — `search()` calls whose result is assigned to a Many2one
    (locations, result package, lot/packaging lookups) now use `limit=1`; duplicated
    barcodes no longer raise a singleton error.
11. **`_compute_qty_picked`** now assigns the field in every branch, as the compute
    contract expects (keeping the scanned value when the line is not picked).

### Remaining technical debt (accepted for now)

- **`action_confirm()` persists `self._cache`** through `_convert_to_write(self._cache)`
  — relies on ORM internals to flush onchange values from the barcode-event environment;
  works in 18.0 but is fragile across versions.
- **Onchange naming** — `onchange_picking_id`, `onchange_package_id`, etc. lack the
  `_onchange_` prefix recommended by OCA guidelines; renaming them is a silent API break
  for downstream overrides, so it is deferred.
- **Direct state writes** — `create_new_stock_move()` sets `state = "assigned"` on
  creation and `action_todo_next()` writes move states directly, bypassing
  `_action_confirm/_action_assign`; intentional for performance.
- The deprecated misspelled aliases should be dropped after one migration cycle.

## 8. Related modules

- `stock_barcodes_picking_batch` (same repo): extends the wizards to batch pickings.
- `stock_barcodes_gs1*`: GS1-128 parsing on top of the `process_barcode_*` pipeline.
