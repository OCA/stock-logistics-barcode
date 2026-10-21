# © 2022 David BEAL @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import Command
from odoo.exceptions import UserError
from odoo.tests import Form

from odoo.addons.sale.tests.common import SaleCommon


class TestSaleInputBarcode(SaleCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.barcode = "5156000000030"
        cls.product.barcode = cls.barcode
        cls.order = cls._create_so(user_id=cls._test_user.id, order_line=[])
        cls.other_company = cls._create_company(name="Other Company")
        cls._create_product(
            name="Other Company Product",
            barcode="5156000000031",
            company_id=cls.other_company.id,
        )
        cls._create_product(
            name="Not Saleable Product", barcode="5156000000032", sale_ok=False
        )
        cls.pricelist = cls._create_pricelist(
            item_ids=[
                Command.create(
                    {
                        "applied_on": "0_product_variant",
                        "product_id": cls.product.id,
                        "compute_price": "fixed",
                        "fixed_price": 15.0,
                    }
                )
            ]
        )

    def _set_update_existing_line(self, value):
        self.env["ir.config_parameter"].sudo().set_bool(
            "sale_input_barcode.sale_barcode_update_existing_line", value
        )

    def test_input_line(self):
        self.order.process_barcode(self.barcode)

        line = self.order.order_line
        self.assertEqual(line.product_id, self.product)
        self.assertEqual(line.product_uom_qty, 1)
        self.assertEqual(line.product_uom_id, self.product.uom_id)
        self.assertEqual(line.price_unit, 20.0)

    def test_input_line_pricelist_price(self):
        self.order.pricelist_id = self.pricelist

        self.order.process_barcode(self.barcode)

        self.assertEqual(self.order.order_line.price_unit, 15.0)

    def test_input_line_new_line(self):
        self.order.process_barcode(self.barcode)
        self.order.process_barcode(self.barcode)

        self.assertEqual(len(self.order.order_line), 2)

    def test_input_line_update_existing_line(self):
        self._set_update_existing_line(True)

        self.order.process_barcode(self.barcode)
        self.order.process_barcode(self.barcode)

        line = self.order.order_line
        self.assertEqual(len(line), 1)
        self.assertEqual(line.product_uom_qty, 2)

    def test_update_existing_line_same_uom_only(self):
        self._set_update_existing_line(True)
        self.order.order_line = [
            Command.create(
                {"product_id": self.product.id, "product_uom_id": self.uom_pack_6.id}
            )
        ]

        self.order.process_barcode(self.barcode)

        self.assertEqual(len(self.order.order_line), 2)
        unit_line = self.order.order_line.filtered(
            lambda line: line.product_uom_id == self.uom_unit
        )
        self.assertEqual(unit_line.product_uom_qty, 1)

    def test_product_of_other_company(self):
        order = self.order.with_context(
            allowed_company_ids=(self.order.company_id | self.other_company).ids
        )
        with self.assertRaises(UserError):
            order.process_barcode("5156000000031")

    def test_product_not_saleable(self):
        with self.assertRaises(UserError):
            self.order.process_barcode("5156000000032")

    def test_on_barcode_scanned(self):
        with Form(self.order) as order_form:
            order_form["_barcode_scanned"] = self.barcode
            order_form["_barcode_scanned"] = self.barcode

        self.assertEqual(len(self.order.order_line), 2)
        self.assertEqual(self.order.order_line.product_id, self.product)

    def test_quotation_only(self):
        self.order._action_cancel()

        with self.assertRaises(UserError):
            self.order.process_barcode(self.barcode)
        self.assertFalse(self.order.order_line)

    def test_on_barcode_scanned_warning(self):
        result = self.order.on_barcode_scanned("0000000000000")

        self.assertEqual(result["warning"]["type"], "notification")
        self.assertFalse(self.order.order_line)

    def test_no_product_found(self):
        with self.assertRaises(UserError):
            self.order.process_barcode("0000000000000")
