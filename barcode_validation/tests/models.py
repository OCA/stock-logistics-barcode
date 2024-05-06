# Copyright 2024 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

from odoo import api, fields, models


class TestModelFake(models.Model):
    _name = "test.model"
    _inherit = ["barcode.validation.mixin"]

    name = fields.Char(required=True)
    barcode = fields.Char(copy=False)

    @api.constrains("barcode")
    def check_barcode_validation(self):
        for record in self.filtered("barcode"):
            record._validate_barcode(record.barcode)
