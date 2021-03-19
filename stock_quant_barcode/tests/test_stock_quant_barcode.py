# Copyright 2021 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestStockQuantBarcode(TransactionCase):
    def setUp(self):
        super().setUp()
        # models
        self.StockLocation = self.env["stock.location"]
        self.Product = self.env["product.product"]
        self.StockProductionLot = self.env["stock.production.lot"]
        self.StockPicking = self.env["stock.picking"]
        self.StockQuant = self.env["stock.quant"]

        # Model Data
        self.company = self.env.user.company_id
        self.partner_agrolite = self.env.ref("base.res_partner_2")
        self.picking_type_in = self.env.ref("stock.picking_type_in")
        self.picking_type_out = self.env.ref("stock.picking_type_out")
        self.picking_type_internal = self.env.ref("stock.picking_type_internal")
        self.supplier_location = self.env.ref("stock.stock_location_suppliers")
        self.customer_location = self.env.ref("stock.stock_location_customers")
        self.stock_location = self.env.ref("stock.stock_location_stock")
        self.categ_unit = self.env.ref("uom.product_uom_categ_unit")
        self.categ_kgm = self.env.ref("uom.product_uom_categ_kgm")

        # warehouse and locations
        self.warehouse = self.env.ref("stock.warehouse0")
        self.location_1 = self.StockLocation.create(
            {
                "name": "Test location 1",
                "usage": "internal",
                "location_id": self.stock_location.id,
            }
        )
        self.location_2 = self.StockLocation.create(
            {
                "name": "Test location 2",
                "usage": "internal",
                "location_id": self.stock_location.id,
            }
        )

        # products
        self.product_tracking = self.Product.create(
            {
                "name": "Product test with lot tracking",
                "type": "product",
                "tracking": "lot",
                "barcode": "8433281006850",
            }
        )
        self.lot_1 = self.StockProductionLot.create(
            {
                "name": "8411822222568",
                "product_id": self.product_tracking.id,
                "company_id": self.company.id,
            }
        )

        self.picking_in_01 = (
            self.env["stock.picking"]
            .with_context(planned_picking=True)
            .create(
                {
                    "location_id": self.supplier_location.id,
                    "location_dest_id": self.stock_location.id,
                    "partner_id": self.partner_agrolite.id,
                    "picking_type_id": self.picking_type_in.id,
                    "move_lines": [
                        (
                            0,
                            0,
                            {
                                "name": self.product_tracking.name,
                                "product_id": self.product_tracking.id,
                                "product_uom_qty": 10,
                                "product_uom": self.product_tracking.uom_id.id,
                                "location_id": self.supplier_location.id,
                                "location_dest_id": self.stock_location.id,
                            },
                        ),
                    ],
                }
            )
        )
        self.picking_in_01.action_confirm()
        self.picking_in_01.action_assign()
        self.picking_in_01.move_line_ids.barcode = "9999"
        self.picking_in_01.move_line_ids.lot_id = self.lot_1
        self.picking_in_01.move_line_ids.qty_done = 10
        self.picking_in_01.action_done()

    def _search_quant(self, barcode):
        return self.StockQuant.search(
            [
                ("barcode", "=", barcode),
                ("location_id.usage", "=", "internal"),
                ("quantity", ">", "0"),
            ]
        )

    def test_write_barcode_move_line(self):
        quant_barcode = self._search_quant("9999")
        self.assertEqual(len(quant_barcode), 1)

    def _move_quants(self, qty, qty_to_move):
        picking = (
            self.env["stock.picking"]
            .with_context(planned_picking=True)
            .create(
                {
                    "location_id": self.stock_location.id,
                    "location_dest_id": self.location_1.id,
                    "picking_type_id": self.picking_type_internal.id,
                    "move_lines": [
                        (
                            0,
                            0,
                            {
                                "name": self.product_tracking.name,
                                "product_id": self.product_tracking.id,
                                "product_uom_qty": qty,
                                "product_uom": self.product_tracking.uom_id.id,
                                "location_id": self.stock_location.id,
                                "location_dest_id": self.location_1.id,
                            },
                        ),
                    ],
                }
            )
        )
        picking.action_confirm()
        picking.action_assign()
        picking.move_line_ids.qty_done = qty_to_move
        picking.action_done()
        return picking

    def test_move_all_quant(self):
        self._move_quants(qty=10, qty_to_move=10)
        quant_barcode = self._search_quant("9999")
        self.assertEqual(len(quant_barcode), 1)

    def test_move_half_quant(self):
        self._move_quants(qty=10, qty_to_move=5)
        quant_barcode = self._search_quant("9999")
        self.assertEqual(len(quant_barcode), 2)

    def test_write_barcode_quant(self):
        quant_barcode = self._search_quant("9999")
        quant_barcode.barcode = "8888"
        quant_barcode = self._search_quant("8888")
        self.assertEqual(len(quant_barcode), 1)
