from odoo import fields, models


class SupplierInfo(models.Model):
    _inherit = "product.supplierinfo"

    barcode = fields.Char(
        "Barcode",
        copy=False,
        help="Article number used by supplier for product identification.",
    )

    _sql_constraints = [
        (
            "barcode_uniq",
            "unique(barcode)",
            "A barcode can only be assigned to one product !",
        )
    ]
