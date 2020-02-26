# Copyright 2020 ForgeFlow S.L. (<http://www.forgeflow.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models

_supported_models = [
    "stock.picking",
    "stock.inventory",
    "product.product",
    "product.template",
]


class PrintRecordLabel(models.TransientModel):
    _inherit = "wizard.print.record.label"

    show_lines = fields.Boolean(compute="_compute_show_lines")

    @api.depends("model")
    def _compute_show_lines(self):
        for wizard in self:
            wizard.show_lines = wizard.model in _supported_models

    @api.returns("stock.move")
    def _prepare_item(self, product_id, qty, lot_barcode=False, package_barcode=False):
        product = self.env["product.product"].browse(product_id)
        values = {
            "product_id": product_id,
            "uom_id": product.uom_id.id,
            "product_qty": qty,
            "label_no": 1.0,
            "product_barcode": product.barcode,
            "lot_barcode": lot_barcode,
            "package_barcode": package_barcode,
        }
        return values

    @api.model
    def default_get(self, fields_list):
        res = super(PrintRecordLabel, self).default_get(fields_list)
        active_model = self.env.context["active_model"]
        if active_model not in _supported_models:
            return res
        if active_model == "stock.picking":
            picking = self.env["stock.picking"].browse(self.env.context["active_id"])
            lines = picking.move_lines
            line_groups = self.env["stock.move.line"].read_group(
                domain=[("move_id", "in", lines.ids)],
                fields=["product_id", "product_qty", "lot_id", "package_id"],
                groupby=["product_id", "product_qty", "lot_id", "package_id"],
                lazy=False,
            )
            items = []
            for line in line_groups:
                item_vals = self._prepare_item(
                    line["product_id"][0],
                    line["product_qty"],
                    line["lot_id"][0] if line["lot_id"] else False,
                    line["package_id"][0] if line["package_id"] else False,
                )
                items.append([0, 0, item_vals])
            res["line_ids"] = items
        elif active_model == "stock.inventory":
            inventory = self.env["stock.inventory"].browse(
                self.env.context["active_id"]
            )
            lines = inventory.move_ids
            line_groups = self.env["stock.move.line"].read_group(
                domain=[("move_id", "in", lines.ids)],
                fields=["product_id", "product_qty", "lot_id", "package_id"],
                groupby=["product_id", "product_qty", "lot_id", "package_id"],
                lazy=False,
            )
            items = []
            for line in line_groups:
                item_vals = self._prepare_item(
                    line["product_id"][0],
                    line["product_qty"],
                    line["lot_id"][0] if line["lot_id"] else False,
                    line["package_id"][0] if line["package_id"] else False,
                )
                items.append([0, 0, item_vals])
            res["line_ids"] = items
        elif active_model == "product.product":
            products = self.env["product.product"].browse(
                self.env.context["active_ids"]
            )
            items = []
            for prod in products:
                item_vals = self._prepare_item(prod.id, 1.0, False, False)
                items.append([0, 0, item_vals])
            res["line_ids"] = items
        elif active_model == "product.template":
            products = self.env["product.template"].browse(
                self.env.context["active_ids"]
            )
            items = []
            for prod in products.mapped("product_variant_ids"):
                item_vals = self._prepare_item(prod.id, 1.0, False, False)
                items.append([0, 0, item_vals])
            res["line_ids"] = items
        return res

    def print_label(self):
        record_model = self.env.context["active_model"]
        if record_model not in ("stock.picking", "product.product", "product.template"):
            return super(PrintRecordLabel, self).print_label()
        record_id = self.env.context["active_id"]
        record = self.env[record_model].browse(record_id)
        for line in self.line_ids:
            for _ in range(line.label_no):
                self.label_id.with_context(mapping=line).print_label(
                    self.printer_id, record
                )


class PrintRecordLabelLines(models.TransientModel):
    _inherit = "wizard.print.record.label.line"

    product_id = fields.Many2one(comodel_name="product.product")
    uom_id = fields.Many2one(comodel_name="uom.uom")
    uom = fields.Char(related="uom_id.name")
    product_barcode = fields.Char()
    lot_barcode = fields.Char()
    package_barcode = fields.Char()
    product_qty = fields.Float()
