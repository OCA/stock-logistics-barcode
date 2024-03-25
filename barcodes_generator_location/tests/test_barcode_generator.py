# Copyright 2017 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo.tests.common import TransactionCase


class TestBarcodeGenerator(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.record = cls.env.ref(
            "barcodes_generator_location.stock_location_barcode",
        )
        cls.record.generate_barcode()

    def test_generate_base(self):
        """It should generate the correct base for the barcode."""
        self.assertEqual(
            self.record.barcode_base,
            1,
        )

    def test_generate_sequence(self):
        """It should generate the correct sequence for the barcode."""
        self.assertEqual(
            self.record.barcode,
            "1190000000014",
        )
