from odoo import fields, models


class BarcodeAction(models.TransientModel):
    _inherit = "barcode.action"

    barcode_scanned = fields.Text("Scanned")
