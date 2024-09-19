# Copyright 2024 Akretion
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import uuid

from psycopg2.errors import UniqueViolation

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase
from odoo.tools.misc import mute_logger

BARCODE_CONSTANT = "123123123"


class TestConstraints(TransactionCase):
    def _create_packaging_unique_barcode(self, product, company_id=False):
        return self.env["product.packaging"].create(
            {
                "name": "test pkg",
                "product_id": product.id,
                "barcode": uuid.uuid4(),
                "company_id": company_id,
            }
        )

    def _create_packaging_constant_barcode(self, product, company_id=False):
        return self.env["product.packaging"].create(
            {
                "name": "test pkg",
                "product_id": product.id,
                "barcode": BARCODE_CONSTANT,
                "company_id": company_id,
            }
        )

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product = cls.env.ref("product.product_product_1")
        cls.company_1 = cls.env.ref("base.main_company")
        cls.company_2 = cls.env["res.company"].create(
            {
                "name": "Company 2",
            }
        )
        cls.product.company_id = False

    def test_same_company_different_barcode(self):
        self._create_packaging_unique_barcode(self.product, self.company_1.id)
        self._create_packaging_unique_barcode(self.product, self.company_1.id)

    def test_same_company_same_barcode(self):
        self._create_packaging_constant_barcode(self.product, self.company_1.id)
        with self.assertRaises(UniqueViolation), mute_logger("odoo.sql_db"):
            self._create_packaging_constant_barcode(self.product, self.company_1.id)

    def test_different_company_same_barcode(self):
        self._create_packaging_constant_barcode(self.product, self.company_1.id)
        self._create_packaging_constant_barcode(self.product, self.company_2.id)

    def test_product_same_barcode_same_company(self):
        self.product.company_id = self.company_1
        self.product.barcode = BARCODE_CONSTANT
        with self.assertRaises(ValidationError):
            self._create_packaging_constant_barcode(self.product, self.company_1.id)

    def test_product_same_barcode_no_company(self):
        self.product.company_id = False
        self.product.barcode = BARCODE_CONSTANT
        with self.assertRaises(ValidationError):
            self._create_packaging_constant_barcode(self.product, self.company_2.id)
