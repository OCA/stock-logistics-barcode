# Copyright 2016 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class Tests(TransactionCase):
    """Tests 'Barcodes Generator for Packages'"""

    @classmethod
    def setUp(cls):
        super().setUpClass()
        cls.package = cls.env.ref(
            "barcodes_generator_package.demo_package",
        )
        cls.barcode_rule = cls.env.ref("barcodes_generator_package.rule_package")

    def test_barcode_generation_based_on_sequence(self):

        self.assertFalse(self.package.barcode_base)
        self.assertFalse(self.package.barcode)

        self.package.barcode_rule_id = self.barcode_rule
        self.assertFalse(self.package.barcode_base)
        self.assertFalse(self.package.barcode)

        self.package.generate_base()
        self.assertEqual(self.package.barcode_base, 1)
        self.assertFalse(self.package.barcode)

        self.package.generate_barcode()
        self.assertEqual(self.package.barcode_base, 1)
        self.assertEqual(self.package.barcode, "1230000000017")
