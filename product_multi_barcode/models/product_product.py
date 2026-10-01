# © 2012-2014 Guewen Baconnier (Camptocamp SA)
# © 2015 Roberto Lizana (Trey)
# © 2016 Pedro M. Baeza
# © 2018 Xavier Jimenez (QubiQ)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
from odoo.fields import Domain


class ProductProduct(models.Model):
    _inherit = "product.product"

    barcode_ids = fields.One2many(
        comodel_name="product.barcode",
        inverse_name="product_id",
        string="Barcodes",
        bypass_search_access=True,
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
        domain = Domain(domain).map_conditions(self._map_barcode_condition)
        return super()._search(domain, *args, **kwargs)

    @api.model
    def _map_barcode_condition(self, condition):
        if condition.field_expr == "barcode":
            return Domain("barcode_ids.name", condition.operator, condition.value)
        return condition
