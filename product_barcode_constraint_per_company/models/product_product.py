# Copyright (C) 2020-Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    _sql_constraints = [
        # Replace constraint with same name
        (
            "barcode_uniq",
            "unique(barcode, company_id)",
            _("A barcode can only be assigned to one product per company !"),
        ),
    ]
