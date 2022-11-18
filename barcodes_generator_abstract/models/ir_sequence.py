from odoo import fields, models


class IrSequence(models.Model):
    _inherit = "ir.sequence"
    last_number = fields.Integer(
        string="Last Number",
        required=True,
        default=1,
        help="Last number of this sequence",
    )
