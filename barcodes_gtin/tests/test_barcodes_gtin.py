# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.exceptions import ValidationError
from odoo.tests import Form
from odoo.tests.common import TransactionCase


class TestBarcodesGtin(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.company
        cls.company.enforce_gtin_barcodes = True
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
            self.product.barcode = barcode

    def test_invalid_gtin_checksums(self):
        """Test that barcodes with bad check digits trigger a ValidationError."""
        invalid_barcodes = [
            "40112005",
            "036000291459",
            "5412345678901",
            "15412345678901",
        ]
        for barcode in invalid_barcodes:
            with self.assertRaises(ValidationError):
                self.product.barcode = barcode

    def test_invalid_gtin_lengths(self):
        """Test that numeric strings of non-GTIN lengths trigger a ValidationError."""
        bad_lengths = ["1234567", "123456789", "123456789012345"]
        for barcode in bad_lengths:
            with self.assertRaises(ValidationError):
                self.product.barcode = barcode

    def test_barcode_onchange_normalization(self):
        """Test that the onchange correctly strips a leading '0' from a 14-digit GTIN."""
        with Form(self.product) as product_form:
            product_form.barcode = "05412345678908"

        self.assertEqual(self.product.barcode, "5412345678908")

    def test_disabled_enforcement(self):
        """Test that constraints are skipped if enforce_gtin_barcodes is disabled."""
        self.company.enforce_gtin_barcodes = False
        self.product.barcode = "INVALID_BARCODE_123"
