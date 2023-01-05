# Copyright (C) 2020-Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import api, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    @api.constrains("barcode")
    def _check_barcode_uniqueness(self):
        return super(
            ProductProduct, self.with_context(search_only_in_company=True)
        )._check_barcode_uniqueness()

    @api.model
    def _search(self, domain, *args, **kwargs):
        if self._context.get("search_only_in_company"):
            company_ids = self.mapped("company_id").ids
            if len(company_ids) > 0:  # Only filter if the source products have company
                company_ids.append(False)  # Also include products without company
                domain.append(("company_id", "in", company_ids))
        return super()._search(domain, *args, **kwargs)
