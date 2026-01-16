# Copyright (C) 2016-Today GRAP (http://www.grap.coop)
# Copyright (C) 2016-Today La Louve (http://www.lalouve.net)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.addons.base.tests.common import BaseCommon


class Tests(BaseCommon):
    """Tests 'Barcodes Generator for Products'"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.ProductTemplate = cls.env["product.template"]
        cls.ProductProduct = cls.env["product.product"]
        cls.barcode_sequence = cls.env["ir.sequence"].create(
            {
                "name": "Barcode Seq.",
                "code": "bar.seq",
                "prefix": "0",
                "padding": 0,
                "company_id": False,
            }
        )
        cls.barcode_rule_manually = cls.env["barcode.rule"].create(
            {
                "name": "Rule - Generate Manually",
                "barcode_nomenclature_id": cls.env.ref(
                    "barcodes.default_barcode_nomenclature"
                ).id,
                "type": "product",
                "sequence": 998,
                "encoding": "ean13",
                "pattern": "20.....{NNNDD}",
                "generate_type": "manual",
                "generate_model": "product.product",
            }
        )

    # Test Section
    def test_01_manual_generation_template(self):
        self.template_mono = self.ProductTemplate.create(
            {
                "name": "Template Mono Variant",
                "barcode_rule_id": self.barcode_rule_manually.id,
                "barcode_base": 54321,
            }
        )
        self.template_mono.generate_barcode()
        self.assertEqual(
            self.template_mono.barcode,
            "2054321000001",
            (
                "Incorrect Manual Barcode Generation for non varianted Template. "
                f"Pattern : {self.template_mono.barcode_rule_id.pattern} - "
                f"Base : {self.template_mono.barcode_base}"
            ),
        )

    def test_02_manual_generation_product(self):
        self.template_multi = self.ProductTemplate.create(
            {"name": "Template Multi Variant"}
        )
        self.product_variant_1 = self.ProductProduct.create(
            {
                "name": "Variant 1",
                "product_tmpl_id": self.template_multi.id,
                "barcode_rule_id": self.barcode_rule_manually.id,
                "barcode_base": 12345,
            }
        )
        self.product_variant_1.generate_barcode()
        self.assertEqual(
            self.product_variant_1.barcode,
            "2012345000001",
            (
                "Incorrect Manual Barcode Generation for varianted Product. "
                f"Pattern : {self.product_variant_1.barcode_rule_id.pattern} - "
                f"Base : {self.product_variant_1.barcode_base}"
            ),
        )

    def test_03_auto_generation_product(self):
        self.template_auto_gen = self.ProductTemplate.create(
            {"name": "Template Test Auto Gen"}
        )
        self.assertFalse(self.template_auto_gen.barcode)
        rule = self.barcode_rule_manually
        rule.sequence_id = self.barcode_sequence
        rule.generate_automate = True
        rule.generate_type = "sequence"
        self.template_auto_gen.barcode_rule_id = rule
        self.assertIsNotNone(self.template_auto_gen.barcode)
