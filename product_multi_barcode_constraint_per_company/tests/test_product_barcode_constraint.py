# Copyright 2023 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from psycopg2 import IntegrityError

from odoo import _
from odoo.exceptions import UserError
from odoo.tools.misc import mute_logger

from odoo.addons.product_barcode_constraint_per_company.tests.common import (
    CommonProductBarcodeConstraintPerCompany,
)


class TestProductBarcodeConstraint(CommonProductBarcodeConstraintPerCompany):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.valid_barcode_1 = "1234567890128123"
        cls.valid_barcode2_1 = "0123456789012123"
        cls.product_test_1 = cls.product_product_obj.create(
            {"name": "Test product 1", "company_id": False}
        )
        cls.product_test_2 = cls.product_product_obj.create(
            {"name": "Test product 2", "company_id": False}
        )

    def test_create_same_company(self):
        """Verifying the Existence of a Product with the Same Barcode within a Single Company"""
        # Create the first product in company_1
        product_1 = self._create_product("Product 1", self.company_1.id)
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
            self._create_product("Product 2", self.company_1.id)

    def test_create_different_company(self):
        """Verify creating a product with the same barcode for different companies"""
        # Create the first product in company_1
        product_1 = self._create_product("Product 1", self.company_1.id)

        # Create the second product in company_2
        product_2 = self._create_product("Product 2", self.company_2.id)

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

    def test_barcode_with_same_company(self):
        """Checking setting same barcode for same companies"""
        self.product_test_1.barcode = self.valid_barcode_1
        self.assertEqual(len(self.product_test_1.barcode_ids), 1)
        self.assertEqual(
            self.product_test_1.barcode_ids.name, self.product_test_1.barcode
        )
        self.product_test_1.company_id = self.company_1.id

        self.product_test_2.company_id = self.company_1.id
        with self.assertRaises(
            UserError,
            msg=_(
                'The Barcode "%(barcode_name)s" already exists for '
                'product "%(product_name)s" in the company %(company_name)s'
            )
            % dict(
                barcode_name=self.valid_barcode_1,
                product_name=self.product_test_1.name,
                company_name=self.product_test_1.company_id.name,
            ),
        ):
            self.product_test_2.barcode = self.valid_barcode_1

    def test_barcodes(self):
        self.product_test_1.barcode = self.valid_barcode_1
        self.product_test_1.company_id = self.company_1.id
        message = (
            _(
                'The Barcode "%(barcode_name)s" already exists for '
                'product "%(product_name)s" in the company %(company_name)s'
            )
            % dict(
                barcode_name=self.valid_barcode2_1,
                product_name=self.product_test_2.name,
                company_name=self.product_test_2.company_id.name,
            ),
        )
        with self.assertRaises(UserError, msg=message):
            self.product_test_2.barcode_ids = [
                (0, 0, {"name": self.valid_barcode2_1}),
                (0, 0, {"name": self.valid_barcode2_1}),
            ]

        self.product_test_2.company_id = self.company_1.id
        with self.assertRaises(UserError, msg=message):
            self.product_test_2.barcode_ids = [
                (0, 0, {"name": self.valid_barcode2_1}),
                (0, 0, {"name": self.valid_barcode2_1}),
            ]
        self.product_test_2.company_id = self.company_2.id
        with self.assertRaises(UserError, msg=message):
            self.product_test_2.barcode_ids = [
                (0, 0, {"name": self.valid_barcode2_1}),
                (0, 0, {"name": self.valid_barcode2_1}),
            ]
        with self.assertRaises(UserError, msg=message):
            self.product_test_2.barcode_ids = [
                (0, 0, {"name": self.valid_barcode2_1}),
                (0, 0, {"name": self.valid_barcode_1}),
            ]

        with self.assertRaises(UserError, msg=message):
            self.product_test_2.barcode_ids = [
                (0, 0, {"name": self.valid_barcode_1}),
                (0, 0, {"name": self.valid_barcode2_1}),
            ]
