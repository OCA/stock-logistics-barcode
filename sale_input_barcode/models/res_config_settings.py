from odoo import fields, models


class ResConfigSettings(models.TransientModel):

    _inherit = "res.config.settings"

    sale_barcode_update_existing_line = fields.Boolean(
        string="Increase quantity instead of creating a new line",
        config_parameter="sale_input_barcode.sale_barcode_update_existing_line",
        default=False,
    )
