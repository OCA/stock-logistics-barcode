# -*- coding: utf-8 -*-
# Copyright 2016-2017 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


EAN14_VALID = [
    '12345678911230',
    '12345278911333',
    '56734527891139',
]


EAN14_INVALID = [
    '12335678911230',
    '56734527891131',
    'abcsdeferfrfgr',
    '2345658911239'
]


class TestBarcodeNomenclature(TransactionCase):

    def setUp(self):
        super(TestBarcodeNomenclature, self).setUp()
        self.model = self.env['barcode.nomenclature']

    def test_ean14_valid(self):
        """ It should return proper checksum for EAN-14 """
        for ean in EAN14_VALID:
            self.assertEqual(
                int(ean[-1]),
                self.model.ean14_checksum(ean),
            )

    def test_ean14_invalid(self):
        """ It should properly handle invalid checksum invalid EAN-14 """
        for ean in EAN14_INVALID:
            try:
                expect = int(ean[-1])
            except ValueError:
                # -1 is returned from ValueError
                expect = 0
            self.assertNotEqual(
                expect,
                self.model.ean14_checksum(ean),
            )

    def test_check_encoding_ean14_valid(self):
        """ It should properly identify valid EAN-14 """
        for ean in EAN14_VALID:
            self.assertTrue(
                self.model.check_encoding(ean, 'ean14'),
                'Failed EAN validation on valid %s' % ean
            )

    def test_check_encoding_ean14_invalid(self):
        """ It should properly identify invalid EAN-14 """
        for ean in EAN14_INVALID:
            self.assertFalse(
                self.model.check_encoding(ean, 'ean14'),
                'Passed EAN validation on invalid %s' % ean
            )

    def test_check_encoding_any(self):
        """ It should return result of super """
        self.assertTrue(self.model.check_encoding('1234', 'any'))
