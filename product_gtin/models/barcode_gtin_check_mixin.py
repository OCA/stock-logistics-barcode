# Copyright 2004-2011 Tiny SPRL (<http://tiny.be>)
# Copyright 2010-2011 Camptocamp Austria (<http://www.camptocamp.at>)
# Copyright 2016 ACSONE SA/NV (<http://acsone.eu>)
# Copyright 2021 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import barcodenumber

from odoo import _, api, models
from odoo.exceptions import ValidationError


class BarcodeGtincheckMixin(models.AbstractModel):
    _name = "barcode.gtin_check.mixin"
    _description = "Barcode Gtin check mixin"
    _barcode_field = "barcode"

    @api.constrains(_barcode_field)
    def _check_barcode(self):
        barcode_field = self._barcode_field
        for record in self:
            if record[barcode_field]:
                record._check_code(record[barcode_field])

    @api.model
    def _check_ean8(self, code):
        return barcodenumber.check_code("ean8", code)

    @api.model
    def _check_isbn10(self, code):
        return barcodenumber.check_code("isbn10", code)

    @api.model
    def _check_upc(self, code):
        return barcodenumber.check_code("upc", code)

    @api.model
    def _check_ean13(self, code):
        return barcodenumber.check_code("ean13", code)

    _DICT_CHECK_CODE_TYPE = {
        8: "ean8",
        10: "isbn10",
        12: "upc",
        13: "ean13",
    }
    _DICT_CHECK_FUNCTIONS = {
        "ean8": _check_ean8,
        "isbn10": _check_isbn10,
        "upc": _check_upc,
        "ean13": _check_ean13,
    }

    @api.model
    def _check_code(self, code):
        nb_digit = len(code)
        if nb_digit in self._DICT_CHECK_CODE_TYPE:
            code_type = self._DICT_CHECK_CODE_TYPE[nb_digit]
            if self.company_id[
                "check_code_type_%s" % code_type
            ] and not self._DICT_CHECK_FUNCTIONS[code_type](self, code):
                raise ValidationError(_("EAN/GTIN format is not a valid format"))
