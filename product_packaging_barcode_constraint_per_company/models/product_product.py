# Copyright 2024 Akretion
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class ProductProduct(models.Model):

    _inherit = "product.product"

    @api.model
    def _search(self, domain, *args, **kwargs):
        company_ids = self.env.context.get("search_only_in_pkg_company")
        if company_ids:
            if len(company_ids) > 0:  # Only filter if the source products have company
                company_ids.append(False)  # Also include products without company
                domain.append(("company_id", "in", company_ids))
        return super()._search(domain, *args, **kwargs)
