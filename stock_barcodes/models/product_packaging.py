# Copyright 2018 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import models, fields


class ProductPackaging(models.Model):
    _inherit = "product.packaging"

    barcode = fields.Char(
        'Barcode', copy=False,
        help="Barcode used for packaging identification."
    )
