# © 2012-2014 Guewen Baconnier (Camptocamp SA)
# © 2015 Roberto Lizana (Trey)
# © 2016 Pedro M. Baeza
# © 2018 Xavier Jimenez (QubiQ)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    barcode_ids = fields.One2many(
        comodel_name="product.barcode",
        inverse_name="product_id",
        string="Barcodes",
    )
    barcode = fields.Char(
        string="Main barcode",
        compute="_compute_barcode",
        store=True,
        inverse="_inverse_barcode",
        compute_sudo=True,
    )

    @api.depends("barcode_ids.name", "barcode_ids.sequence")
    def _compute_barcode(self):
        for product in self:
            product.barcode = product.barcode_ids[:1].name

    def _inverse_barcode(self):
        """Store the product's barcode value in the barcode model."""
        barcodes_to_unlink = self.env["product.barcode"]
        create_barcode_vals_list = []
        for product in self:
            if product.barcode_ids:
                product.barcode_ids[0].name = product.barcode
            elif not product.barcode:
                barcodes_to_unlink |= product.barcode_ids
            else:
                create_barcode_vals_list.append(product._prepare_barcode_vals())
        if barcodes_to_unlink:
            barcodes_to_unlink.unlink()
        if create_barcode_vals_list:
            self.env["product.barcode"].create(create_barcode_vals_list)

    def _prepare_barcode_vals(self):
        self.ensure_one()
        return {
            "product_id": self.id,
            "name": self.barcode,
        }

    @api.model
    def _search(self, domain, *args, **kwargs):
        domain = domain.copy()
        for key, sub_domain in enumerate(domain):
            if sub_domain[0] == "barcode":
                domain[key] = self._get_barcode_subdomain(sub_domain)
        return super()._search(domain, *args, **kwargs)

    def _get_barcode_subdomain(self, sub_domain):
        barcode_operator = sub_domain[1]
        barcode_value = sub_domain[2]
        sub_domain = ("barcode_ids.name", barcode_operator, barcode_value)
        return sub_domain
