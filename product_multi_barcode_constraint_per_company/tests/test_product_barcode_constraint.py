# Copyright 2023 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import types

from psycopg2 import IntegrityError

from odoo.tests.common import tagged
from odoo.tools.misc import mute_logger

from odoo.addons.product_barcode_constraint_per_company.tests.test_module import (
    TestModule,
)

from .. import void


@tagged("post_install", "-at_install")
class TestProductBarcodeConstraintInherit(TestModule):
    def test_void(self):
        """Verify the type of the result of the void method call."""
        result = void(None)
        self.assertIsInstance(
            result,
            types.FunctionType,
            msg="Expecting a FunctionType result, but got {result_type}".format(
                result_type=type(result)
            ),
        )

    def test_create_same_company(self):
        """Verifying the Existence of a Product with the Same Barcode within a Single Company"""
        # Create the first product in company_1
        product_1 = self._create_product("Product 1", self.company_1)

        # Check if the company_id of the product matches self.company_1
        self.assertEqual(
            product_1.company_id,
            self.company_1,
            msg="Product company ID must be equal to ID #{company}".format(
                company=self.company_1.id
            ),
        )

        # Check if the company_id of the product_tmpl_id matches self.company_1
        self.assertEqual(
            product_1.product_tmpl_id.company_id,
            self.company_1,
            msg="Product company ID must be equal to ID # {company}".format(
                company=self.company_1.id
            ),
        )

        # Try to create a second product with the same barcode in company_1
        # and expect an IntegrityError
        with mute_logger("odoo.sql_db"), self.assertRaises(
            IntegrityError,
            msg="A barcode can only be assigned to one product per company !",
        ):
            self._create_product("Product 2", self.company_1)

    def test_create_different_company(self):
        """Verify creating a product with the same barcode for different companies"""
        # Create the first product in company_1
        product_1 = self._create_product("Product 1", self.company_1)

        # Create the second product in company_2
        product_2 = self._create_product("Product 2", self.company_2)

        # Check that the products belong to different companies
        self.assertNotEqual(
            product_1.company_id,
            product_2.company_id,
            msg="Products should belong to different companies",
        )

        # Check that the products have the same barcode
        self.assertEqual(
            product_1.barcode,
            product_2.barcode,
            msg="Products should have the same barcode",
        )
