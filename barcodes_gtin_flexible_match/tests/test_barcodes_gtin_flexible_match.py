# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo.tests.common import TransactionCase

from ..tools.barcodes_gtin import get_gtin_variants, is_valid_gtin_barcode


class TestBarcodesGtinFlexibleMatch(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(
            context=dict(
                cls.env.context,
                tracking_disable=True,
            )
        )
        cls.company = cls.env.company
        cls.company.barcode_flexible_gtin_match = True
        cls.product = cls.env["product.product"].create({"name": "GTIN Test Product"})

    def test_valid_gtin_barcodes(self):
        """Test that valid GTIN-8, GTIN-12, GTIN-13, and GTIN-14 pass constraints."""
        valid_barcodes = [
            "40112008",
            "036000291452",
            "5412345678908",
            "15412345678905",
        ]
        for barcode in valid_barcodes:
            self.assertTrue(is_valid_gtin_barcode(barcode))

    def test_invalid_gtin_checksums(self):
        """Test that barcodes with bad check digits trigger a ValidationError."""
        invalid_barcodes = [
            "40112005",
            "036000291459",
            "5412345678901",
            "15412345678901",
        ]
        for barcode in invalid_barcodes:
            self.assertFalse(is_valid_gtin_barcode(barcode))

    def test_get_gtin_variants(self):
        gtin13_barcode = "5412345678908"
        variants = get_gtin_variants(gtin13_barcode)
        variants.sort(key=lambda x: len(x))
        self.assertEqual(variants, [gtin13_barcode, "0" + gtin13_barcode])

        gtin14_barcode = "05412345678908"
        variants = get_gtin_variants(gtin14_barcode)
        variants.sort(key=lambda x: len(x))
        self.assertEqual(variants, [gtin14_barcode[1:], gtin14_barcode])

    def test_search_flexible_barcode_match_equal_operator(self):
        gtin_13_barcode = "5412345678908"
        self.product.barcode = gtin_13_barcode
        res = self.env["product.product"].search(
            [("barcode", "=", "0" + gtin_13_barcode)]
        )
        self.assertEqual(res, self.product)

        gtin_14_barcode = "05412345678908"
        self.product.barcode = gtin_13_barcode
        res = self.env["product.product"].search(
            [("barcode", "=", gtin_14_barcode[1:])]
        )
        self.assertEqual(res, self.product)

    def test_search_flexible_barcode_match_like_operators(self):
        gtin_13_barcode = "5412345678908"
        gtin_14_barcode = "05412345678908"
        self.product.barcode = gtin_13_barcode

        res_ilike = self.env["product.product"].search(
            [("barcode", "ilike", f"%{gtin_14_barcode}%")]
        )
        self.assertEqual(res_ilike, self.product)

        res_like = self.env["product.product"].search(
            [("barcode", "like", gtin_14_barcode)]
        )
        self.assertEqual(res_like, self.product)

        res_equal_ilike = self.env["product.product"].search(
            [("barcode", "=ilike", gtin_14_barcode)]
        )
        self.assertEqual(res_equal_ilike, self.product)

        res_equal_like = self.env["product.product"].search(
            [("barcode", "=like", gtin_14_barcode)]
        )
        self.assertEqual(res_equal_like, self.product)
