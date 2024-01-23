from odoo.exceptions import UserError
from odoo.tests.common import SavepointCase


class TestProductProductBarcodeWizard(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.barcode_rule = cls.env.ref(
            "barcode_generator_product_variant.product_generated_barcode_demo"
        )
        cls.test_product = cls.env.ref("product.product_product_4_product_template")

    def test_generate_missing_barcodes(self):
        self.assertFalse(any(self.test_product.mapped("product_variant_ids.barcode")))
        self.assertTrue(self.test_product.has_missing_barcodes)

        self.barcode_rule.is_default = True
        wizard = self.env["product.product.barcode.wizard"].create(
            {
                "product_tmpl_id": self.test_product.id,
            }
        )

        # Barcode rule should be the default one
        self.assertEqual(self.barcode_rule, wizard.barcode_rule_id)

        wizard.action_generate_barcodes()
        self.assertTrue(all(self.test_product.mapped("product_variant_ids.barcode")))
        self.assertFalse(self.test_product.has_missing_barcodes)

    def test_default_rule(self):
        new_barcode_rule = self.barcode_rule.copy({"name": "New Barcode Rule"})

        self.barcode_rule.is_default = True

        # Setting more than one rule as default should raise an error
        with self.assertRaises(UserError):
            new_barcode_rule.is_default = True
