# Copyright 2024 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ProductPackaging(models.Model):
    _inherit = "product.packaging"

    print_one_label_by_item = fields.Boolean(
        help="If checked, Odoo take into account the units included in the packaging "
        "to compute number of labels"
    )
