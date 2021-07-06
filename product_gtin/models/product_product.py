# Copyright 2004-2011 Tiny SPRL (<http://tiny.be>)
# Copyright 2010-2011 Camptocamp Austria (<http://www.camptocamp.at>)
# Copyright 2016 ACSONE SA/NV (<http://acsone.eu>)
# Copyright 2021 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import models


class ProductProduct(models.Model):
    _name = "product.product"
    _inherit = ["barcode.gtin_check.mixin", "product.product"]
