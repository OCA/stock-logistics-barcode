# Copyright 2021 Tecnativa - Carlos Roca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.tests.common import TransactionCase


class TestStockPickingProductBarcodeReportSecondaryUnit(TransactionCase):
    def setUp(self):
        super().setUp()
        self.supplier_location = self.env.ref("stock.stock_location_suppliers")
        self.stock_location = self.env.ref("stock.stock_location_stock")
        primary_uom = self.env.ref("uom.product_uom_kgm")
        self.product_barcode = self.env["product.product"].create(
            {
                "name": "Test Product 1",
                "type": "product",
                "barcode": "1001",
                "uom_id": primary_uom.id,
                "uom_po_id": primary_uom.id,
                "qty_available": 300,
                "secondary_uom_ids": [
                    (
                        0,
                        0,
                        {
                            "code": "TB",
                            "name": "Test Box",
                            "uom_id": self.env.ref("uom.product_uom_unit").id,
                            "factor": 10,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "code": "TP",
                            "name": "Test Package",
                            "uom_id": self.env.ref("uom.product_uom_unit").id,
                            "factor": 20,
                        },
                    ),
                ],
            }
        )
        partner = self.env["res.partner"].create({"name": "Test Partner"})
        picking_receipt_type = self.env.ref("stock.picking_type_in")
        self.picking = self.env["stock.picking"].create(
            {
                "location_id": self.supplier_location.id,
                "location_dest_id": self.stock_location.id,
                "partner_id": partner.id,
                "picking_type_id": picking_receipt_type.id,
                "move_ids_without_package": [
                    (
                        0,
                        0,
                        {
                            "name": "Test 01",
                            "product_id": self.product_barcode.id,
                            "quantity_done": 50,
                            "product_uom": self.product_barcode.uom_id.id,
                        },
                    )
                ],
            }
        )
        self.picking.button_validate()

    def _create_print_wizard(self):
        self.wizard = (
            self.env["stock.picking.print"]
            .with_context(
                {"active_ids": [self.picking.id], "active_model": "stock.picking"}
            )
            .create({})
        )

    def test_wizard_creation(self):
        self._create_print_wizard()
        self.wizard._onchange_picking_ids()
        self.assertEqual(1, len(self.wizard.product_print_moves.ids))
        line = self.wizard.product_print_moves[0]
        self.assertEqual(line.label_qty, 5)
        self.assertEqual(line.product_id.id, self.product_barcode.id)

    def test_wizard_creation_with_secondary_uom_move(self):
        sml = self.picking.move_line_ids
        sml.secondary_uom_id = self.product_barcode.secondary_uom_ids[1]
        sml.secondary_uom_qty = 2
        self._create_print_wizard()
        self.wizard._onchange_picking_ids()
        self.assertEqual(1, len(self.wizard.product_print_moves.ids))
        line = self.wizard.product_print_moves[0]
        self.assertEqual(line.label_qty, 2)
