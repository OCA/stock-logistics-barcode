# Copyright (C) 2016-Today GRAP (http://www.grap.coop)
# Copyright (C) 2016-Today La Louve (http://www.lalouve.net)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class Tests(TransactionCase):
    """Tests 'Barcodes Generator for Products'"""

    def setUp(self):
        super(Tests, self).setUp()
        self.template_obj = self.env['product.template']
        self.product_obj = self.env['product.product']

    # Test Section
    def test_01_manual_generation_template(self):
        self.template_mono = self.template_obj.browse(self.ref(
            'barcodes_generator_product.product_template_mono_variant'))
        self.assertEqual(
            self.template_mono.barcode, "2000050000003",
            "Incorrect Manual Barcode Generation for non varianted Template."
            " Pattern : %s - Base : %s" % (
                self.template_mono.barcode_rule_id.pattern,
                self.template_mono.barcode_base))

    def test_02_manual_generation_product(self):
        self.product_variant_1 = self.product_obj.browse(self.ref(
            'barcodes_generator_product.product_product_variant_1'))
        self.assertEqual(
            self.product_variant_1.barcode, "2010001000006",
            "Incorrect Manual Barcode Generation for varianted Product."
            " Pattern : %s - Base : %s" % (
                self.product_variant_1.barcode_rule_id.pattern,
                self.product_variant_1.barcode_base))

    def test_03_create_with_custom_barcode_automatic_rule(self):
        """When automatic generation is enabled, you should still be able to
        create a product with a custom barcode.
        """
        rule = self.env.ref("barcodes_generator_product.product_generated_barcode")
        rule.generate_type = "sequence"
        rule.generate_sequence()
        rule.generate_automate = True

        custom_barcode = "2000042003500"
        product = self.env["product.product"].create(
            {"name": "Foo", "barcode": custom_barcode}
        )
        self.assertEqual(product.barcode, custom_barcode)

    def test_04_create_with_custom_rule_automatic_rule(self):
        """When automatic generation is enabled, you should still be able to
        create a product with a custom barcode rule.
        """
        rule = self.env.ref("barcodes_generator_product.product_generated_barcode")
        rule.generate_type = "sequence"
        rule.generate_sequence()
        rule.generate_automate = True

        other_rule = self.env["barcode.rule"].create(
            {
                "barcode_nomenclature_id": self.env.ref(
                    "barcodes.default_barcode_nomenclature"
                ).id,
                "name": "Custom Rule",
                "type": "product",
                "sequence": 999,
                "encoding": "ean13",
                "pattern": "30.....{NNNDD}",
            }
        )

        product = self.env["product.product"].create({
            "name": "Foo", "barcode_rule_id": other_rule.id,
        })
        self.assertEqual(product.barcode_rule_id, other_rule)
        self.assertEqual(product.barcode, False)

    def test_05_create_template_with_custom_barcode_automatic_rule(self):
        """When automatic generation is enabled, you should still be able to
        create a product template with a custom barcode, and its variant should
        have that barcode.
        """
        rule = self.env.ref("barcodes_generator_product.product_generated_barcode")
        rule.generate_type = "sequence"
        rule.generate_sequence()
        rule.generate_automate = True

        custom_barcode = "2000042003500"
        template = self.env["product.template"].create(
            {"name": "Foo", "barcode": custom_barcode}
        )
        self.assertEqual(template.barcode, custom_barcode)
        # NOTE: I've not been able to achieve the result of the commented-out
        # lines.
        # self.assertEqual(template.barcode_rule_id, False)
        self.assertEqual(template.product_variant_id.barcode, custom_barcode)
        # self.assertEqual(template.product_variant_id.barcode_rule_id, False)

    def test_06_create_template_with_custom_rule_automatic_rule(self):
        """When automatic generation is enabled, you should still be able to
        create a product template with a custom barcode rule, and its variant
        should have that rule and no barcode.
        """
        rule = self.env.ref("barcodes_generator_product.product_generated_barcode")
        rule.generate_type = "sequence"
        rule.generate_sequence()
        rule.generate_automate = True

        other_rule = self.env["barcode.rule"].create(
            {
                "barcode_nomenclature_id": self.env.ref(
                    "barcodes.default_barcode_nomenclature"
                ).id,
                "name": "Custom Rule",
                "type": "product",
                "sequence": 999,
                "encoding": "ean13",
                "pattern": "30.....{NNNDD}",
            }
        )

        template = self.env["product.template"].create({
            "name": "Foo", "barcode_rule_id": other_rule.id,
        })
        self.assertEqual(template.barcode_rule_id, other_rule)
        self.assertEqual(template.product_variant_id.barcode_rule_id, other_rule)
        self.assertEqual(template.barcode, False)
        self.assertEqual(template.barcode_base, False)
        self.assertEqual(template.product_variant_id.barcode, False)
        self.assertEqual(template.product_variant_id.barcode_base, False)
