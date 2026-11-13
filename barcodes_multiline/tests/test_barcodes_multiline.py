# Copyright 2021 Therp BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import TransactionCase


class TestBarcodesMultiline(TransactionCase):
    def test_onchange_preserves_multiline_input(self):
        wizard = self.env["barcodes_multiline.demo_wizard"].new({})
        wizard._barcode_scanned = "SKU: A123\nSERIAL: 456"
        wizard._on_barcode_scanned()
        self.assertEqual(wizard.text, "SKU: A123\nSERIAL: 456")
        self.assertFalse(wizard._barcode_scanned)
