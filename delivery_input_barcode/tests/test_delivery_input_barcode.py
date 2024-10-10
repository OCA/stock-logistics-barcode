# © 2022 David BEAL @ Akretion
# © 2024 David Palanca @ Grupo Isonor

# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests import TransactionCase


class Test(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.stock_location = cls.env.ref("stock.stock_location_stock")

    def test_input_line(self):
        self.env = self.env(context=dict(self.env.context, tracking_disable=True))
        barcode = "5156000000030"
        product = self.env["product.product"].create(
            {
                "name": "barcode test",
                "barcode": barcode,
            }
        )
        picking_stock = self.env["stock.picking"].create(
            {
                "location_id": self.stock_location.id,
                "location_dest_id": self.stock_location.id,
                "picking_type_id": self.env.ref("stock.picking_type_internal").id,
            }
        )

        picking_stock.action_move_barcode(barcode)
        self.assertIn(product, picking_stock.move_lines.mapped("product_id"))
