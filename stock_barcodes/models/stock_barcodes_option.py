# Copyright 2019 Sergio Teruel <sergio.teruel@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class StockBarcodesOptionGroup(models.Model):
    _name = "stock.barcodes.option.group"
    _description = "Options group for barcode interface"

    name = fields.Char()
    code = fields.Char(
        help="Short code of the group. It is not only a label: the interface "
        "checks it to apply specific behaviors, so keep IN for receipts, OUT "
        "for deliveries and REL for relocation groups"
    )
    option_ids = fields.One2many(
        comodel_name="stock.barcodes.option", inverse_name="option_group_id", copy=True
    )
    barcode_guided_mode = fields.Selection(
        [("guided", "Guided")],
        string="Mode",
        help="When guided mode is selected, information will appear with the "
        "movement to be processed",
    )
    manual_entry = fields.Boolean(
        string="Manual entry",
        help="Default value when open scan interface",
    )
    manual_entry_field_focus = fields.Char(
        help="Set field to set focus when manual entry mode is enabled",
        default="location_id",
    )
    confirmed_moves = fields.Boolean(
        string="Confirmed moves",
        help="It allows to work with movements without reservation "
        "(Without detailed operations)",
    )
    show_pending_moves = fields.Boolean(
        string="Show pending moves", help="Shows a list of movements to process"
    )
    source_pending_moves = fields.Selection(
        [("move_line_ids", "Detailed operations"), ("move_ids", "Operations")],
        default="move_line_ids",
        help="Origin of the data to generate the movements to process",
    )
    ignore_filled_fields = fields.Boolean(
        string="Ignore filled fields",
        help="If checked, the required fields that already have a value are "
        "skipped when resolving a scanned barcode, instead of being overwritten",
    )
    auto_put_in_pack = fields.Boolean(
        string="Auto put in pack", help="Auto put in pack before picking validation"
    )
    is_manual_qty = fields.Boolean(
        help="If it is checked, it always shows the product quantity field in edit mode"
    )
    is_manual_confirm = fields.Boolean(
        help="If it is marked, the movement must always be confirmed from a button"
    )
    allow_negative_quant = fields.Boolean(
        help="If it is checked, it will allow the creation of movements that "
        "generate negative stock"
    )
    fill_fields_from_lot = fields.Boolean(
        help="If checked, the fields in the interface will be filled from "
        "the scanned lot"
    )
    ignore_quant_location = fields.Boolean(
        help="If it is checked, quant location will be ignored when reading lot/package",
    )
    group_key_for_todo_records = fields.Char(
        help="You can establish a list of fields that will act as a grouping "
        "key to generate the movements to be process.\n"
        "The object variable is used to refer to the source record\n"
        "For example, object.location_id,object.product_id,object.lot_id"
    )
    auto_lot = fields.Boolean(
        string="Get lots automatically",
        help="If checked the lot will be set automatically with the same "
        "removal startegy",
    )
    create_lot = fields.Boolean(
        string="Create lots if not match",
        help="If checked the lot will created automatically with the scanned barcode "
        "if not exists ",
    )
    show_detailed_operations = fields.Boolean(
        help="If checked the picking detailed operations are displayed",
    )
    keep_screen_values = fields.Boolean(
        help="If checked the wizard values are kept until the pending move is completed",
    )
    accumulate_read_quantity = fields.Boolean(
        help="If checked quantity will be accumulated to the existing record instead of "
        "overwrite it with the new quantity value",
    )
    display_notification = fields.Boolean(
        string="Display Odoo notifications",
        help="If checked, the interface messages (barcode not found, required "
        "field empty, ...) are also shown as Odoo notifications",
    )
    use_location_dest_putaway = fields.Boolean(
        string="Use location dest. putaway",
        help="If checked, a destination location that is required but still "
        "empty is computed with the putaway strategy of the transfer "
        "destination instead of being asked for",
    )
    location_field_to_sort = fields.Selection(
        selection=[
            ("location_id", "Origin Location"),
            ("location_dest_id", "Destination Location"),
        ],
        help="Location used to sort the movements to process. If not set, the "
        "destination location is used for incoming and internal transfers, and "
        "the origin location for the other ones",
    )
    display_read_quant = fields.Boolean(
        string="Read items on inventory mode",
        help="Default value of the Read items switch of the inventory "
        "interface, which lists either the items already counted or the ones "
        "that are not counted yet",
    )
    no_increase_qty_done = fields.Boolean(
        string="Do not increase qty done on each scan",
        help="If checked, the done quantity of the movement is replaced by "
        "the quantity of the scan instead of being added to the one already "
        "registered. Only used in picking operations",
    )
    show_form_scan = fields.Boolean(
        default=True,
        help="If checked, the scan fields are always displayed. If not, they "
        "are only displayed while manual entry is enabled",
    )

    def get_option_value(self, field_name, attribute):
        option = self.option_ids.filtered(lambda op: op.field_name == field_name)[:1]
        return option[attribute]


class StockBarcodesOption(models.Model):
    _name = "stock.barcodes.option"
    _description = "Options for barcode interface"
    _order = "step, sequence, id"

    sequence = fields.Integer(
        default=100,
        help="Order in which the options of a step are evaluated to resolve a "
        "scanned barcode. The first option that matches wins, so more specific "
        "fields should come first (a package before a product, for example)",
    )
    name = fields.Char(
        help="Label used for this field in the interface messages, both when "
        "it asks to scan it and when it reports that it is required"
    )
    option_group_id = fields.Many2one(
        comodel_name="stock.barcodes.option.group", ondelete="cascade"
    )
    field_name = fields.Char(
        help="Technical name of the barcode interface field this option refers "
        "to, e.g. product_id, lot_id, location_id or product_qty.\n"
        "A scanned barcode is resolved by calling the process_barcode_<field "
        "name> method, so a field without such a method will never be filled "
        "by a scan"
    )
    filled_default = fields.Boolean(
        help="If checked, the field is pre-filled with the value of the "
        "movement to process each time the interface presents a new one, "
        "instead of being emptied. When the interface is opened from an "
        "operation type or a transfer, the locations are pre-filled with its "
        "default ones.\n"
        "On the quantity field it also disables the automatic 1 unit per "
        "scan, leaving the quantity to the user"
    )
    forced = fields.Boolean(
        help="If checked, the value already set in the field prevails: it is "
        "not overwritten with the location of a scanned lot or package, the "
        "search for a package is restricted to it, and a detailed operation "
        "with a different location is not reused.\n"
        "In guided mode it also rejects a scan whose product, lot or location "
        "does not match the movement being guided"
    )
    to_scan = fields.Boolean(
        help="If checked, a barcode scanned on this step can fill this field. "
        "Fields that are not scannable can still be filled manually"
    )
    required = fields.Boolean(
        help="If checked, the movement cannot be processed while the field is "
        "empty. Required options also drive the navigation: the interface moves "
        "to the step of the first required option that is still empty"
    )
    clean_after_done = fields.Boolean(
        help="If checked, the field is emptied once the movement is confirmed "
        "and when the Clean values button is pressed. Leave it unchecked to "
        "keep the value between scans, as is usually done with the source "
        "location"
    )
    message = fields.Char()
    step = fields.Integer(
        help="Groups the options into successive screens. Only the options of "
        "the current step are candidates for the barcode being scanned"
    )
