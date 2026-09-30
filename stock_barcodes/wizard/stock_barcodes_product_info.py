# Copyright 2026 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class WizStockBarcodesProductInfo(models.TransientModel):
    _name = "wiz.stock.barcodes.product.info"
    _description = "Product information for the barcode scan screen"

    res_model = fields.Char(required=True)
    res_id = fields.Many2oneReference(model_field="res_model", required=True)
    location_field = fields.Selection(
        [
            ("location_id", "Source Location"),
            ("location_dest_id", "Destination Location"),
        ],
        required=True,
    )
    product_id = fields.Many2one(comodel_name="product.product", readonly=True)
    show_product_info = fields.Boolean(default=True)
    product_uom_id = fields.Many2one(related="product_id.uom_id")
    qty_available = fields.Float(
        string="On Hand", digits="Product Unit of Measure", readonly=True
    )
    incoming_qty = fields.Float(
        string="Incoming", digits="Product Unit of Measure", readonly=True
    )
    outgoing_qty = fields.Float(
        string="Outgoing", digits="Product Unit of Measure", readonly=True
    )
    virtual_available = fields.Float(
        string="Forecasted", digits="Product Unit of Measure", readonly=True
    )
    line_ids = fields.One2many(
        comodel_name="wiz.stock.barcodes.product.info.location",
        inverse_name="wiz_id",
        readonly=True,
    )

    def _get_scan_wizard(self):
        self.ensure_one()
        return self.env[self.res_model].browse(self.res_id)


class WizStockBarcodesProductInfoLocation(models.TransientModel):
    _name = "wiz.stock.barcodes.product.info.location"
    _description = "Product stock in a location for the barcode scan screen"
    _order = "sequence, id"

    wiz_id = fields.Many2one(
        comodel_name="wiz.stock.barcodes.product.info",
        required=True,
        ondelete="cascade",
    )
    sequence = fields.Integer()
    location_id = fields.Many2one(comodel_name="stock.location", readonly=True)
    quantity = fields.Float(digits="Product Unit of Measure", readonly=True)
    product_uom_id = fields.Many2one(related="wiz_id.product_uom_id")

    def action_select(self):
        self.ensure_one()
        self.wiz_id._get_scan_wizard()._set_location_from_stock(
            self.wiz_id.location_field, self.location_id
        )
        return {"type": "ir.actions.act_window_close"}
