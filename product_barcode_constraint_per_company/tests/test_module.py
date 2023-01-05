# Copyright (C) 2019 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase
from odoo.tools.misc import mute_logger


class TestModule(TransactionCase):
    def setUp(self):
        super().setUp()

        self.ResCompany = self.env["res.company"]
        self.ProductProduct = self.env["product.product"]
        self.company_1 = self.ResCompany.create({"name": "Company 1"})
        self.company_2 = self.ResCompany.create({"name": "Company 2"})

    # Test Section
    def test_create_same_company(self):
        self._create_product("Product 1", self.company_1.id)

        with self.assertRaises(ValidationError), mute_logger("odoo.sql_db"):
            product2 = self._create_product("Product 2", self.company_1.id)
            product2.flush_recordset()

    def test_create_different_company(self):
        self._create_product("Product 1", self.company_1.id)
        self._create_product("Product 2", self.company_2.id)

    def test_create_no_company(self):
        self._create_product("Product 1", self.company_1.id)
        with self.assertRaises(ValidationError), mute_logger("odoo.sql_db"):
            product2 = self._create_product("Product 2", None)
            product2.flush_recordset()

    def test_create_no_company_bis(self):
        self._create_product("Product 1", None)
        with self.assertRaises(ValidationError), mute_logger("odoo.sql_db"):
            product2 = self._create_product("Product 2", self.company_2.id)
            product2.flush_recordset()

    def _create_product(self, name, company_id):
        vals = {
            "name": name,
            "company_id": company_id,
            "barcode": "978020137962",
        }
        return self.ProductProduct.create(vals)
