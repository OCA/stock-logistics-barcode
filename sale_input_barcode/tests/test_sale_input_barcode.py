# © 2022 David BEAL @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.exceptions import UserError
from odoo.tests import TransactionCase


class Test(TransactionCase):
    def test_input_line(self):
        barcode = "5156000000030"
        product = self.env["product.product"].create(
            {
                "name": "barcode test",
                "barcode": barcode,
            }
        )
        sale = self.env["sale.order"].create(
            {
                "partner_id": self.env["res.partner"]
                .create({"name": "Test Customer"})
                .id,
            }
        )

        sale.action_sale_line_barcode(barcode)

        self.assertIn(product, sale.order_line.mapped("product_id"))

    def test_input_line_update_existing_line(self):
        barcode = "5156000000031"
        product = self.env["product.product"].create(
            {
                "name": "barcode test update",
                "barcode": barcode,
            }
        )
        sale = self.env["sale.order"].create(
            {
                "partner_id": self.env["res.partner"]
                .create({"name": "Test Customer"})
                .id,
            }
        )

        self.env["ir.config_parameter"].sudo().set_param(
            "sale_input_barcode.sale_barcode_update_existing_line",
            "True",
        )

        sale.action_sale_line_barcode(barcode)
        sale.action_sale_line_barcode(barcode)

        line = sale.order_line.filtered(lambda line: line.product_id == product)
        self.assertEqual(len(line), 1)
        self.assertEqual(line.product_uom_qty, 2)

    def test_on_barcode_scanned(self):
        barcode = "5156000000032"
        product = self.env["product.product"].create(
            {
                "name": "barcode test scanned",
                "barcode": barcode,
            }
        )
        sale = self.env["sale.order"].create(
            {
                "partner_id": self.env["res.partner"]
                .create({"name": "Test Customer"})
                .id,
            }
        )

        sale.on_barcode_scanned(barcode)

        self.assertIn(product, sale.order_line.mapped("product_id"))

    def test_no_product_found(self):
        sale_line = self.env["sale.order.line"]

        with self.assertRaises(UserError):
            sale_line._process_barcode_on_product_line("0000000000000")
