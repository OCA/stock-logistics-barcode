# © 2016 Pedro M. Baeza
# © 2018 Xavier Jimenez (QubiQ)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.exceptions import ValidationError
from odoo.fields import Domain
from odoo.tests import TransactionCase, tagged

from ..hooks import clear_multi_variant_template_barcodes, post_init_hook


@tagged("post_install", "-at_install")
class TestProductMultiBarcode(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Product 1
        cls.product = cls.env["product.product"]
        cls.product_1 = cls.product.create({"name": "Test product 1"})
        cls.valid_barcode_1 = "1234567890128"
        cls.valid_barcode2_1 = "0123456789012"
        # Product 2
        cls.product_2 = cls.product.create({"name": "Test product 2"})
        cls.valid_barcode_2 = "9780471117094"
        cls.valid_barcode2_2 = "4006381333931"

    def test_set_main_barcode(self):
        self.product_1.barcode = self.valid_barcode_1
        self.assertEqual(len(self.product_1.barcode_ids), 1)
        self.assertEqual(self.product_1.barcode_ids.name, self.product_1.barcode)

    def test_set_incorrect_barcode(self):
        self.product_1.barcode = self.valid_barcode_1
        # Insert duplicated EAN13
        with self.assertRaisesRegex(
            ValidationError,
            (
                f'The Barcode "{self.valid_barcode_1}" already exists '
                f'for product "{self.product_1.name}"'
            ),
        ):
            self.product_1.barcode_ids = [(0, 0, {"name": self.valid_barcode_1})]

    def test_post_init_hook(self):
        self.env.cr.execute(
            """
            UPDATE product_product
            SET barcode = %s
            WHERE id = %s""",
            (self.valid_barcode_1, self.product_1.id),
        )
        post_init_hook(self.env)
        self.product_1.invalidate_recordset()
        self.assertEqual(len(self.product_1.barcode_ids), 1)
        self.assertEqual(self.product_1.barcode_ids.name, self.valid_barcode_1)

    def test_search(self):
        self.product_1.barcode_ids = [
            (0, 0, {"name": self.valid_barcode_1}),
            (0, 0, {"name": self.valid_barcode2_1}),
        ]
        self.product_2.barcode_ids = [
            (0, 0, {"name": self.valid_barcode_2}),
            (0, 0, {"name": self.valid_barcode2_2}),
        ]
        products = self.product.search([("barcode", "=", self.valid_barcode_1)])
        self.assertEqual(len(products), 1)
        self.assertEqual(products, self.product_1)
        products = self.product.search([("barcode", "=", self.valid_barcode2_1)])
        self.assertEqual(len(products), 1)
        self.assertEqual(products, self.product_1)
        products = self.product.search(
            [
                "|",
                ("barcode", "=", self.valid_barcode2_1),
                ("barcode", "=", self.valid_barcode2_2),
            ]
        )
        self.assertEqual(len(products), 2)
        products = self.product.search(
            [("product_tmpl_id", "any", [("name", "=", self.product_1.name)])]
        )
        self.assertIn(self.product_1, products)

    def test_search_with_internal_domain_operator(self):
        self.product_1.barcode_ids = [(0, 0, {"name": self.valid_barcode_1})]
        domain = Domain(
            "product_tmpl_id", "any!", [("name", "=", "no-such-product-name")]
        ) | Domain("barcode", "=", self.valid_barcode_1)
        self.assertEqual(self.product.search(domain), self.product_1)

    def test_search_template_by_secondary_barcode(self):
        self.product_1.barcode_ids = [
            (0, 0, {"name": self.valid_barcode_1}),
            (0, 0, {"name": self.valid_barcode2_1}),
        ]
        template = self.product_1.product_tmpl_id
        templates = self.env["product.template"]
        self.assertEqual(
            templates.search([("barcode", "=", self.valid_barcode2_1)]), template
        )
        self.assertEqual(
            templates.search([("barcode", "ilike", self.valid_barcode2_1[2:9])]),
            template,
        )

    def test_barcode_on_variant_of_multi_variant_template(self):
        attribute = self.env["product.attribute"].create(
            {
                "name": "Test size",
                "value_ids": [(0, 0, {"name": "S"}), (0, 0, {"name": "M"})],
            }
        )
        template = self.env["product.template"].create(
            {
                "name": "Test multi variant",
                "attribute_line_ids": [
                    (
                        0,
                        0,
                        {
                            "attribute_id": attribute.id,
                            "value_ids": [(6, 0, attribute.value_ids.ids)],
                        },
                    )
                ],
            }
        )
        variant_1, variant_2 = template.product_variant_ids
        variant_1.barcode = self.valid_barcode_1
        variant_2.barcode_ids = [
            (0, 0, {"name": self.valid_barcode_2}),
            (0, 0, {"name": self.valid_barcode2_2}),
        ]
        self.assertEqual(variant_1.barcode, self.valid_barcode_1)
        self.assertEqual(
            self.env["product.template"].search(
                [("barcode", "=", self.valid_barcode2_2)]
            ),
            template,
        )

    def test_multi_variant_template_has_no_barcode(self):
        template = self.product_1.product_tmpl_id
        self.product_1.barcode = self.valid_barcode_1
        self.assertEqual(template.barcode, self.valid_barcode_1)
        attribute = self.env["product.attribute"].create(
            {
                "name": "Test color",
                "value_ids": [(0, 0, {"name": "Red"}), (0, 0, {"name": "Blue"})],
            }
        )
        template.attribute_line_ids = [
            (
                0,
                0,
                {
                    "attribute_id": attribute.id,
                    "value_ids": [(6, 0, attribute.value_ids.ids)],
                },
            )
        ]
        self.assertEqual(len(template.product_variant_ids), 2)
        self.env.flush_all()
        template.invalidate_recordset()
        self.assertFalse(template.barcode)
        # The old template barcode no longer blocks other products
        self.product_2.barcode = self.valid_barcode_1
        self.assertEqual(self.product_2.barcode, self.valid_barcode_1)
        template.barcode = self.valid_barcode_2
        self.env.flush_all()
        template.invalidate_recordset()
        self.assertFalse(template.barcode)

    def test_variant_list_barcode_readonly(self):
        arch = self.product.get_views(
            [(self.env.ref("product.product_product_tree_view").id, "list")]
        )["views"]["list"]["arch"]
        self.assertRegex(arch, r'<field name="barcode"[^>]*readonly="True"')

    def test_post_init_hook_clears_multi_variant_template_barcode(self):
        attribute = self.env["product.attribute"].create(
            {
                "name": "Test material",
                "value_ids": [(0, 0, {"name": "Wood"}), (0, 0, {"name": "Iron"})],
            }
        )
        template = self.env["product.template"].create(
            {
                "name": "Test hook multi variant",
                "attribute_line_ids": [
                    (
                        0,
                        0,
                        {
                            "attribute_id": attribute.id,
                            "value_ids": [(6, 0, attribute.value_ids.ids)],
                        },
                    )
                ],
            }
        )
        single_template = self.product_1.product_tmpl_id
        self.product_1.barcode = self.valid_barcode_1
        self.env.flush_all()
        self.env.cr.execute(
            "UPDATE product_template SET barcode = %s WHERE id = %s",
            (self.valid_barcode_2, template.id),
        )
        clear_multi_variant_template_barcodes(self.env.cr)
        self.env.invalidate_all()
        self.assertFalse(template.barcode)
        self.assertEqual(single_template.barcode, self.valid_barcode_1)
