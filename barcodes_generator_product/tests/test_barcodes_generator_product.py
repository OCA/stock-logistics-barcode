# Copyright (C) 2016-Today GRAP (http://www.grap.coop)
# Copyright (C) 2016-Today La Louve (http://www.lalouve.net)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo.tests.common import SavepointCase


class TestBarcodeGeneratorProduct(SavepointCase):
    """Tests 'Barcodes Generator for Products'"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.template_obj = cls.env["product.template"]
        cls.product_obj = cls.env["product.product"]
        cls.barcode_rule = cls.env.ref(
            "barcodes_generator_product.product_generated_barcode"
        )

    # Test Section
    def test_01_manual_generation_template(self):
        template_mono = self.env.ref(
            "barcodes_generator_product.product_template_mono_variant"
        )
        template_mono.write(
            {"barcode_rule_id": self.barcode_rule.id, "barcode_base": 50}
        )
        template_mono.generate_barcode()
        self.assertEqual(
            template_mono.barcode,
            "2000050000003",
            "Incorrect Manual Barcode Generation for non varianted Template."
            " Pattern : %s - Base : %s"
            % (
                template_mono.barcode_rule_id.pattern,
                template_mono.barcode_base,
            ),
        )

    def test_02_manual_generation_product(self):
        product_variant_1 = self.env.ref(
            "barcodes_generator_product.product_product_variant_1"
        )
        product_variant_1.write(
            {"barcode_rule_id": self.barcode_rule.id, "barcode_base": 10001}
        )
        product_variant_1.generate_barcode()
        self.assertEqual(
            product_variant_1.barcode,
            "2010001000006",
            "Incorrect Manual Barcode Generation for varianted Product."
            " Pattern : %s - Base : %s"
            % (
                product_variant_1.barcode_rule_id.pattern,
                product_variant_1.barcode_base,
            ),
        )
