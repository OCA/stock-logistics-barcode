# Copyright 2020 Carlos Roca <carlos.roca@tecnativa.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestStockPickingProductBarcodeReport(TransactionCase):
    def setUp(self):
        super().setUp()
        self.supplier_location = self.env.ref("stock.stock_location_suppliers")
        self.stock_location = self.env.ref("stock.stock_location_stock")
        self.product_barcode = self.env["product.product"].create(
            {"name": "Test Product 1", "type": "product", "barcode": "1001"}
        )
        self.product_no_barcode = self.env["product.product"].create(
            {"name": "Test Product 2", "type": "product"}
        )
        partner = self.env["res.partner"].create({"name": "Test Partner"})
        self.picking = self.env["stock.picking"].create(
            {
                "location_id": self.supplier_location.id,
                "location_dest_id": self.stock_location.id,
                "partner_id": partner.id,
                "picking_type_id": 1,  # Operation type Receipts
                "move_ids_without_package": [
                    (
                        0,
                        0,
                        {
                            "name": "Test 01",
                            "product_id": self.product_barcode.id,
                            "product_uom_qty": 20,
                            "product_uom": self.product_barcode.uom_id.id,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": "Test 02",
                            "product_id": self.product_no_barcode.id,
                            "product_uom_qty": 10,
                            "product_uom": self.product_barcode.uom_id.id,
                        },
                    ),
                ],
            }
        )
        self.picking.action_confirm()
        self.wizard = (
            self.env["stock.picking.print"]
            .with_context(
                {"active_ids": [self.picking.id], "active_model": "stock.picking"}
            )
            .create({})
        )

    def test_wizard_creation(self):
        self.wizard._onchange_picking_ids()
        self.assertEqual(1, len(self.wizard.product_print_moves.ids))
        line = self.wizard.product_print_moves[0]
        self.assertEqual(line.label_qty, 1)
        self.assertEqual(line.product_id.id, self.product_barcode.id)
        # This two sentences are added just for check that not throw an exception
        self.wizard.barcode_format = "gs1_128"
        self.wizard.print_labels()
