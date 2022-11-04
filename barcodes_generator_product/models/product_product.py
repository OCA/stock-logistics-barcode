# Copyright (C) 2014-Today GRAP (http://www.grap.coop)
# Copyright (C) 2016-Today La Louve (http://www.lalouve.net)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class ProductProduct(models.Model):
    _name = "product.product"
    _inherit = ["product.product", "barcode.generate.mixin"]

    def show_generate_multi_barcodes(self):
        view_id = self.env.ref(
            "barcodes_generator_product.view_generate_multi_barcodes_form"
        ).id
        wizard = self.env["barcode.multiple.generator.wizard"].create({})
        product_ids = self.env["product.product"].browse(self.env.context["active_ids"])
        wizard.product_ids = product_ids.filtered(lambda x: not x.barcode).ids
        wizard.ignored_products = " - ".join(
            [prod.name for prod in product_ids if prod.barcode]
        )
        return {
            "type": "ir.actions.act_window",
            "res_model": "barcode.multiple.generator.wizard",
            "res_id": wizard.id,
            "view_mode": "form",
            "view_id": view_id,
            "target": "new",
        }
