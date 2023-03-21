# Copyright 2016 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import SavepointCase


class TestBarcodeGenerator(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestBarcodeGenerator, cls).setUpClass()
        cls.record = cls.env.ref(
            "barcodes_generator_package.product_packaging_barcode",
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
            "1230000000017",
        )
