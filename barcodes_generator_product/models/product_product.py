# Copyright (C) 2014-Today GRAP (http://www.grap.coop)
# Copyright (C) 2016-Today La Louve (http://www.lalouve.net)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class ProductProduct(models.Model):
    _name = "product.product"
    _inherit = ["product.product", "barcode.generate.mixin"]

    def write(self, vals):
        barcode_rule_id = self.mapped("product_tmpl_id.barcode_rule_id")
        if barcode_rule_id:
            vals["barcode_rule_id"] = barcode_rule_id[0]
        return super(ProductProduct, self).write(vals)
