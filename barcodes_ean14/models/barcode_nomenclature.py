# -*- coding: utf-8 -*-
# Copyright 2016-2017 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import re

from odoo import models


class BarcodeNomenclature(models.Model):
    _inherit = 'barcode.nomenclature'

    def ean14_checksum(self, barcode):
        """ It performs EAN-14 checksum operation
        :param barcode: Barcode string to validate, including check digit
        :return: ``int`` representing calculated checksum
        """
        if len(barcode) != 14:
            return -1
        barcode = barcode[:-1]
        total = 0
        for (idx, digit) in enumerate(barcode):
            try:
                digit = int(digit)
            except ValueError:
                return -1
            if idx % 2 == 1:
                total += digit
            else:
                total += (3 * digit)
        check_digit = (10 - (total % 10)) % 10
        return check_digit

    def check_encoding(self, barcode, encoding):
        """ It adds additional types to the core encodings """
        if encoding == 'ean14':
            try:
                check_digit = int(barcode[-1])
            except ValueError:
                return False
            return all([
                re.match(r'^\d+$', barcode),
                self.ean14_checksum(barcode) == check_digit,
            ])
        return super(BarcodeNomenclature, self).check_encoding(
            barcode, encoding,
        )
