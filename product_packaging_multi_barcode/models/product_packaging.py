# Copyright 2023 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class ProductPackaging(models.Model):
    _inherit = "product.packaging"

    barcode_ids = fields.One2many(
        comodel_name="product.barcode",
        inverse_name="packaging_id",
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
        for packaging in self:
            packaging.barcode = packaging.barcode_ids[:1].name

    def _inverse_barcode(self):
        """Store the packaging's barcode value in the barcode model."""
        barcodes_to_unlink = self.env["product.barcode"]
        create_barcode_vals_list = []
        for packaging in self:
            if packaging.barcode_ids:
                packaging.barcode_ids[0].name = packaging.barcode
            elif not packaging.barcode:
                barcodes_to_unlink |= packaging.barcode_ids
            else:
                create_barcode_vals_list.append(packaging._prepare_barcode_vals())
        if barcodes_to_unlink:
            barcodes_to_unlink.unlink()
        if create_barcode_vals_list:
            self.env["product.barcode"].create(create_barcode_vals_list)

    def _prepare_barcode_vals(self):
        self.ensure_one()
        return {
            "packaging_id": self.id,
            "name": self.barcode,
        }
