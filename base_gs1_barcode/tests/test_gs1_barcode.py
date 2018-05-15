# -*- coding: utf-8 -*-
# © 2017 Acsone SA/NV (http://www.acsone.eu)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import odoo.tests.common as common


class TestGs1Barcode(common.TransactionCase):

    def setUp(self):
        super(TestGs1Barcode, self).setUp()

    def test_gs1_barcode(self):
        GS = '\x1D'
        PREFIX = ''
        # AI 01 (GTIN, fixed length)
        gtin = '03400933816759'
        # AI 17 (expiry date) - day 0 will be replaced by last day of month
        expiry = '140500'
        # AI 10 (lot number, variable length)
        lot = 'B04059A'
        # AI 310 (Net Weight in Kg, 5 decimals)
        weight = '006385'

        barcode = PREFIX + '01' + gtin + '17' + expiry + '10' + lot + GS + \
            '3105' + weight
        result = self.env['gs1_barcode'].decode(barcode)

        self.assertEqual(len(result), 4, "The barcode should decode to 4 AIs")
        self.assertEqual(result.get('01'), gtin,
                         "The GTIN should be %s" % gtin)
        self.assertEqual(result.get('17'), '2014-05-31',
                         "The expiry date should be %s" % expiry)
        self.assertEqual(result.get('10'), lot, "The lot should be %s" % lot)
        self.assertEqual(result.get('310'), 0.06385,
                         "The weight should be %s" % weight)
