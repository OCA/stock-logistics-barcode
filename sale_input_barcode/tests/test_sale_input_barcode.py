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

    def test_on_barcode_scanned(self):
        with Form(self.order) as order_form:
            order_form["_barcode_scanned"] = self.barcode
            order_form["_barcode_scanned"] = self.barcode

        self.assertEqual(len(self.order.order_line), 2)
        self.assertEqual(self.order.order_line.product_id, self.product)

    def test_no_product_found(self):
        with self.assertRaises(UserError):
            self.order.process_barcode("0000000000000")
