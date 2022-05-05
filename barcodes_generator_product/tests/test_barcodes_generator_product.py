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
        self.sequence_test_1 = self.env["ir.sequence"].create(
            {
                "name": "Sequence test 1",
                "implementation": "standard",
                "padding": 4,
                "number_increment": 1,
                "number_next_actual": 1,
            }
        )
        self.barcode_rule = self.env["barcode.rule"].create(
            {
                "name": "Product Rule Test",
                "barcode_nomenclature_id": self.env.ref(
                    "barcodes.default_barcode_nomenclature"
                ).id,
                "type": "product",
                "sequence": self.sequence_test_1.id,
                "encoding": "ean13",
                "pattern": "20.....{NNNDD}",
                "generate_type": "manual",
                "generate_model": "product.product",
            }
        )
        self.barcode_rule_2 = self.env["barcode.rule"].create(
            {
                "name": "Product Rule Test",
                "barcode_nomenclature_id": self.env.ref(
                    "barcodes.default_barcode_nomenclature"
                ).id,
                "type": "product",
                "sequence": 0,
                "sequence_id": self.sequence_test_1.id,
                "encoding": "ean13",
                "pattern": "12345678....",
                "padding": 4,
                "generate_type": "sequence",
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

    def test_03_assigned_barcode_variants(self):
        self.template_multi = self.template_obj.create(
            {
                "name": "Template Multi Variant",
            }
        )
        self.product_variant_1 = self.product_obj.create(
            {
                "name": "Variant 1",
                "product_tmpl_id": self.template_multi.id,
            }
        )
        self.product_variant_2 = self.product_obj.create(
            {
                "name": "Variant 2",
                "product_tmpl_id": self.template_multi.id,
            }
        )
        self.template_multi.write({"barcode_rule_id": self.barcode_rule_2.id})

        self.assertEqual(
            self.product_variant_1.barcode_rule_id, self.template_multi.barcode_rule_id
        )
        self.assertEqual(
            self.product_variant_2.barcode_rule_id, self.template_multi.barcode_rule_id
        )

    def test_04_assigned_barcode_variants(self):
        self.template_multi = self.template_obj.create(
            {
                "name": "Template Multi Variant",
            }
        )
        self.product_variant_1 = self.product_obj.create(
            {
                "name": "Variant 1",
                "product_tmpl_id": self.template_multi.id,
                "barcode": 123456,
            }
        )
        self.product_variant_2 = self.product_obj.create(
            {
                "name": "Variant 1",
                "product_tmpl_id": self.template_multi.id,
            }
        )
        self.template_multi.write({"barcode_rule_id": self.barcode_rule_2.id})
        self.template_multi.action_generate_barcode()

        self.assertEqual(self.product_variant_1.barcode, "123456")
        self.assertNotEqual(self.product_variant_2.barcode, False)

        self.registry.reset_changes()
