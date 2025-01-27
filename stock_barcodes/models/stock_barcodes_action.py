# Copyright 2019 Sergio Teruel <sergio.teruel@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import base64
import re
from io import BytesIO

import barcode
from barcode.writer import ImageWriter

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools.safe_eval import safe_eval

REGEX = {
    "context": r"^[^\s].*[^\s]$|^$",
    "barcode": "^[a-zA-Z0-9-]+$",
}
FIELDS_NAME = {"barcode_options": "barcode_option_group_id"}


class StockBarcodesAction(models.Model):
    _name = "stock.barcodes.action"
    _description = "Actions for barcode interface"
    _order = "sequence, id"

    name = fields.Char(translate=True)
    active = fields.Boolean(default=True)
    sequence = fields.Integer(default=100)
    action_window_id = fields.Many2one(
        comodel_name="ir.actions.act_window", string="Action window"
    )
    context = fields.Char()
    key_shortcut = fields.Integer()
    key_char_shortcut = fields.Char()
    icon_class = fields.Char()
    barcode = fields.Char()
    barcode_image = fields.Image(
        "Barcode image",
        readonly=True,
        compute="_compute_barcode_image",
        attachment=True,
    )

    count_elements = fields.Integer(default=0, compute="_compute_count_elements")

    @api.constrains("barcode")
    def _constrains_barcode(self):
        for action in self:
            if not re.match(REGEX.get("barcode", False), action.barcode):
                raise ValidationError(
                    _(
                        " The barcode {} is not correct."
                        "Use numbers, letters and dashes, without spaces."
                        "E.g. 15753, BC-5789,er-56 "
                        ""
                    ).format(action.barcode)
                )
            all_barcode = [bar for bar in action.mapped("barcode") if bar]
            domain = [("barcode", "in", all_barcode)]
            matched_actions = self.sudo().search(domain, order="id")
            if len(matched_actions) > len(all_barcode):
                raise ValidationError(
                    _(
                        """ Barcode has already been assigned to the action(s): {}."""
                    ).format(", ".join(matched_actions.mapped("name")))
                )

    def _generate_barcode(self):
        barcode_type = barcode.get_barcode_class("code128")
        buffer = BytesIO()
        barcode_instance = barcode_type(self.barcode, writer=ImageWriter())
        barcode_instance.write(buffer)
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue())
        return image_base64

    @api.depends("barcode")
    def _compute_barcode_image(self):
        for action in self:
            if action.barcode:
                action.barcode_image = action._generate_barcode()
            else:
                action.barcode_image = False

    @api.constrains("context")
    def _constrains_context(self):
        if self.context and not bool(
            re.match(REGEX.get("context", False), self.context)
        ):
            raise ValidationError(_("There can be no spaces at the beginning or end."))

    def _count_elements(self):
        domain = []
        if self.context:
            context_values = self.context.strip("{}").split(",")

            def _map_context_values(x):
                field_values = x.split(":")
                field_name = field_values[0].split("search_default_")
                if len(field_name) > 1:
                    field_name = field_name[1].strip("'")
                    field_value_format = field_values[1].replace("'", "").strip()
                    field_value = (
                        int(field_value_format)
                        if field_value_format.isdigit()
                        else field_value_format
                    )
                    if hasattr(
                        self.action_window_id.res_model,
                        FIELDS_NAME.get(field_name, field_name),
                    ):
                        return (
                            "{}".format(FIELDS_NAME.get(field_name, field_name)),
                            "=",
                            field_value,
                        )
                    else:
                        return False
                else:
                    return ()

            domain = [
                val_domain
                for val_domain in list(
                    map(lambda x: _map_context_values(x), context_values)
                )
            ]
            search_count = (
                list(filter(lambda x: x, domain))
                if all(val_d is True for val_d in domain)
                else []
            )
            return (
                self.env[self.action_window_id.res_model].search_count(search_count)
                if self.action_window_id.res_model
                else 0
            )
        return 0

    @api.depends("context")
    def _compute_count_elements(self):
        for barcode_action in self:
            barcode_action.count_elements = (
                barcode_action._count_elements()
                if "search_default_" in barcode_action.context
                else 0
            )

    def open_action(self):
        action = self.action_window_id.sudo().read()[0]
        action_context = safe_eval(action["context"])
        ctx = self.env.context.copy()
        if action_context:
            ctx.update(action_context)
        if self.context:
            ctx.update(safe_eval(self.context))
        if action_context.get("inventory_mode", False):
            action = self.open_inventory_action(ctx)
        else:
            action["context"] = ctx

        return action

    def open_inventory_action(self, ctx):
        option_group = self.env.ref(
            "stock_barcodes.stock_barcodes_option_group_inventory"
        )
        vals = {
            "option_group_id": option_group.id,
            "manual_entry": option_group.manual_entry,
            "display_read_quant": option_group.display_read_quant,
        }
        if option_group.get_option_value("location_id", "filled_default"):
            vals["location_id"] = (
                self.env["stock.warehouse"].search([], limit=1).lot_stock_id.id
            )
        wiz = self.env["wiz.stock.barcodes.read.inventory"].create(vals)
        action = self.env["ir.actions.actions"]._for_xml_id(
            "stock_barcodes.action_stock_barcodes_read_inventory"
        )
        action["res_id"] = wiz.id
        action["context"] = ctx
        return action

    def print_barcodes(self):
        report_action = self.env.ref(
            "stock_barcodes.action_report_barcode_actions"
        ).report_action(None, data={})
        return report_action
