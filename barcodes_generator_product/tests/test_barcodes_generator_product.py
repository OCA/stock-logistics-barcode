# Copyright (C) 2016-Today GRAP (http://www.grap.coop)
# Copyright (C) 2016-Today La Louve (http://www.lalouve.net)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class Tests(TransactionCase):
    """Tests 'Barcodes Generator for Products'"""

    def setUp(self):
        super().setUp()
        self.template_obj = self.env["product.template"]
        self.product_obj = self.env["product.product"]
        self.barcode_rule = self.env["barcode.rule"].create(
            {
                "name": "Product Rule Test",
                "barcode_nomenclature_id": self.env.ref(
                    "barcodes.default_barcode_nomenclature"
                ).id,
                "type": "product",
                "sequence": 999,
                "encoding": "ean13",
                "pattern": "20.....{NNNDD}",
                "generate_type": "manual",
                "generate_model": "product.product",
            }
        )

    # Test Section
    def test_01_manual_generation_template(self):
        self.template_mono = self.template_obj.create(
            {
                "name": "Template Mono Variant",
                "barcode_rule_id": self.barcode_rule.id,
                "barcode_base": 50,
            }
        )
        self.template_mono.generate_barcode()
        self.assertEqual(
            self.template_mono.barcode,
            "2000050000003",
            "Incorrect Manual Barcode Generation for non varianted Template."
            " Pattern : %s - Base : %s"
            % (
                self.template_mono.barcode_rule_id.pattern,
                self.template_mono.barcode_base,
            ),
        )

    def test_02_manual_generation_product(self):
        self.template_multi = self.template_obj.create(
            {"name": "Template Multi Variant"}
        )
        self.product_variant_1 = self.product_obj.create(
            {
                "name": "Variant 1",
                "product_tmpl_id": self.template_multi.id,
                "barcode_rule_id": self.barcode_rule.id,
                "barcode_base": 10001,
            }
        )
        self.product_variant_1.generate_barcode()
        self.assertEqual(
            self.product_variant_1.barcode,
            "2010001000006",
            "Incorrect Manual Barcode Generation for varianted Product."
            " Pattern : %s - Base : %s"
            % (
                self.product_variant_1.barcode_rule_id.pattern,
                self.product_variant_1.barcode_base,
            ),
        )

    def test_03_auto_generation_product(self):
        self.template_auto_gen = self.template_obj.create(
            {"name": "Template Test Auto Gen"}
        )
        self.assertFalse(self.template_auto_gen.barcode)
        rule = self.env.ref("barcodes_generator_product.product_generated_barcode")
        rule.sequence_id = self.env.ref(
            "barcodes_generator_product.seq_product_generated_barcode"
        )
        rule.generate_automate = True
        rule.generate_type = "sequence"
        self.template_auto_gen.barcode_rule_id = rule
        self.assertIsNotNone(self.template_auto_gen.barcode)
