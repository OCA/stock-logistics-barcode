# Copyright 2019 Sergio Teruel <sergio.teruel@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class StockBarcodesOptionGroup(models.Model):
    _name = "stock.barcodes.option.group"
    _description = "Options group for barcode interface"

    name = fields.Char()
    code = fields.Char(
        help="Technical code of the group. Some codes change the behavior of the "
        "scan screen:\n"
        "- IN: reading a lot or package does not take the source location from "
        "the stock.\n"
        "- OUT: reading a lot or package does not propose the quantity in stock.\n"
        "- REL: quantities over the demand are accepted without asking for "
        "confirmation."
    )
    option_ids = fields.One2many(
        comodel_name="stock.barcodes.option", inverse_name="option_group_id", copy=True
    )
    barcode_guided_mode = fields.Selection(
        [("guided", "Guided")],
        string="Mode",
        help="Guided: the screen proposes one pending move at a time and rejects "
        "a product, lot or location different from the expected one when its "
        "option is forced.\n"
        "Empty (free mode): barcodes can be read in any order.",
    )
    manual_entry = fields.Boolean(
        string="Manual entry",
        help="Open the scan screen in manual entry mode, with the fields editable "
        "and each reading confirmed from a button.",
    )
    manual_entry_on_edit = fields.Boolean(
        string="Manual entry on edit",
        help="Switch to manual entry when a pending move is edited with the "
        "pencil icon, so its values can be changed before confirming.",
    )
    manual_entry_field_focus = fields.Char(
        help="Technical name of the field that gets the focus when switching to "
        "manual entry (e.g. location_id or product_qty).",
        default="location_id",
    )
    confirmed_moves = fields.Boolean(
        string="Confirmed moves",
        help="It allows to work with movements without reservation "
        "(Without detailed operations)",
    )
    show_pending_moves = fields.Selection(
        [
            ("none", "None"),
            ("pending", "Only pending moves"),
            ("all", "All moves, pending and done"),
        ],
        string="Show pending moves",
        help="Shows a list of movements to process",
    )
    source_pending_moves = fields.Selection(
        [("move_line_ids", "Detailed operations"), ("move_ids", "Operations")],
        default="move_line_ids",
        help="Origin of the data to generate the movements to process",
    )
    ignore_filled_fields = fields.Boolean(
        string="Ignore filled fields",
        help="Skip the required options that already have a value when "
        "processing a barcode, so it is matched against the next options of the "
        "step (e.g. a second location barcode sets the destination once the "
        "source is filled).",
    )
    auto_put_in_pack = fields.Boolean(
        string="Auto put in pack",
        help="When a picking of an operation type using this group is validated "
        "and none of its detailed operations has a destination package, put "
        "them in a new package.",
    )
    is_manual_qty = fields.Boolean(
        help="The quantity is always typed by the operator: scans do not set it "
        "and the quantity field stays editable."
    )
    is_manual_confirm = fields.Boolean(
        help="Scans only fill the screen and each reading is confirmed with the "
        "Confirm button, instead of being processed as soon as the required "
        "fields are filled."
    )
    allow_negative_quant = fields.Boolean(
        help="If it is checked, it will allow the creation of movements that "
        "generate negative stock"
    )
    fill_fields_from_lot = fields.Boolean(
        help="When a lot or a product is read, fill the product, lot, package, "
        "owner and location from its stock (only the values common to all its "
        "quants). A lot without stock is rejected unless negative stock is "
        "allowed. Not applied on receipts."
    )
    ignore_quant_location = fields.Boolean(
        help="When the fields are filled from the stock of a lot or package, "
        "keep the location of the screen instead of taking the stock location."
    )
    group_key_for_todo_records = fields.Char(
        help="You can establish a list of fields that will act as a grouping "
        "key to generate the movements to be process.\n"
        "The object variable is used to refer to the source stock move or "
        "stock move line\n"
        "For example, object.location_id,object.product_id,object.lot_id or "
        "object.picking_id,object.product_id"
    )
    auto_lot = fields.Boolean(
        string="Get lots automatically",
        help="Pickings: when a tracked product is read, set the lot already "
        "reserved for it in the location or, if none, the first available lot by "
        "removal strategy. Not applied on receipts.",
    )
    create_lot = fields.Boolean(
        string="Create lots if not match",
        help="Accept a lot name that does not exist yet. The lot is created with "
        "the reading in inventories and when the picking is validated in "
        "transfers.",
    )
    show_detailed_operations = fields.Boolean(
        help="If checked the picking detailed operations are displayed",
    )
    keep_screen_values = fields.Boolean(
        help="""
            If checked the wizard values are kept until
            the pending move is completed
        """,
    )
    accumulate_read_quantity = fields.Boolean(
        string="Accumulate repeated readings",
        help="With manual confirmation, reading the same product, lot or "
        "packaging again before confirming adds one more unit (or packaging) to "
        "the quantity to confirm.",
    )
    display_notification = fields.Boolean(
        string="Display Odoo notifications",
        help="Show a notification when a reading cannot be processed because a "
        "required field is empty.",
    )
    use_location_dest_putaway = fields.Boolean(
        string="Use location dest. putaway",
        help="When the destination location is required and empty, compute it "
        "with the putaway strategy of the picking destination.",
    )
    show_fixed_location_dest = fields.Boolean(
        string="Show fixed dest. location",
        help="Read the destination location already planned on the stock move "
        "line, without recomputing the putaway strategy:\n"
        "- Show it on each pending move of the barcode screen, only for a fixed "
        "putaway (destination without storage category, i.e. independent of the "
        "received quantity).\n"
        "- When scanning a product, reuse the move line already routed by "
        "putaway and keep its destination, instead of creating a duplicate line "
        "at the generic picking destination.",
    )
    location_field_to_sort = fields.Selection(
        selection=[
            ("location_id", "Origin Location"),
            ("location_dest_id", "Destination Location"),
        ],
        help="Location used to sort the pending moves (by X, Y, Z position and "
        "name). If empty, the destination is used for receipts and internal "
        "transfers and the source for the rest.",
    )
    display_read_quant = fields.Boolean(
        string="Read items on inventory mode",
        help="Open the inventory scan screen listing the items already counted "
        "instead of the pending ones.",
    )
    show_stock = fields.Boolean(
        default=False,
        help="Show on the scan screen the quantity of the product available in "
        "the selected location.",
    )
    show_owner = fields.Boolean(
        default=False,
        help="Show the owner field on the scan screen.",
    )
    no_increase_qty_done = fields.Boolean(
        string="Replace quantity on each reading",
        help="A confirmed reading replaces the quantity already recorded instead "
        "of being added to it: the done quantity of the detailed operation in "
        "pickings and the counted quantity in inventories.",
    )
    show_form_scan = fields.Boolean(
        default=True,
        help="Keep the scan fields always visible. If unchecked, they are only "
        "displayed in manual entry.",
    )
    search_picking_from_product = fields.Selection(
        [
            ("first", "First picking"),
            ("last", "Last picking"),
            # ('select', 'Select picking (Not implemented)'),
        ],
        help="When the screen is opened from an operation type, without a "
        "picking, reading a product opens the first or last ready picking of that "
        "type with a move for the product (in the order the moves were created).",
    )
    allow_not_demanded_product = fields.Boolean(
        help="Accept products that are not in the picking demand, adding a new "
        "move for them. If unchecked they are rejected as not demanded."
    )

    def get_option_value(self, field_name, attribute):
        option = self.option_ids.filtered(lambda op: op.field_name == field_name)[:1]
        return option[attribute]


class StockBarcodesOption(models.Model):
    _name = "stock.barcodes.option"
    _description = "Options for barcode interface"
    _order = "step, sequence, id"

    sequence = fields.Integer(default=100)
    name = fields.Char()
    option_group_id = fields.Many2one(
        comodel_name="stock.barcodes.option.group", ondelete="cascade"
    )
    field_name = fields.Char(help="Technical name of the scan screen field")
    filled_default = fields.Boolean(
        help="Fill the field with the value of the pending move (guided mode) or "
        "of the picking or operation type when the screen is opened."
    )
    forced = fields.Boolean(
        help="Guided mode: reject a value different from the one of the pending "
        "move."
    )
    to_scan = fields.Boolean(
        help="The field can be filled by reading a barcode in its step."
    )
    required = fields.Boolean(
        help="A reading is not processed while the field is empty. The step of "
        "the first empty required field is the current step of the screen."
    )
    clean_after_done = fields.Boolean(
        help="Empty the field after each processed reading."
    )
    message = fields.Char()
    step = fields.Integer(
        help="Order in which the fields are asked. Only the fields to scan of the "
        "current step are matched against a barcode."
    )
