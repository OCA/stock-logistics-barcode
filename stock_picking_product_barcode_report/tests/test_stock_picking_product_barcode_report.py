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
        self.package = self.env["stock.quant.package"].create({"name": "Pack-Test"})
        partner = self.env["res.partner"].create({"name": "Test Partner"})
        self.picking = self.env["stock.picking"].create(
            {
                "location_id": self.supplier_location.id,
                "location_dest_id": self.stock_location.id,
                "partner_id": partner.id,
                "picking_type_id": self.env.ref(
                    "stock.picking_type_in"
                ).id,  # Operation type Receipts
                "move_ids_without_package": [
                    (
                        0,
                        0,
                        {
                            "name": "Test 01",
                            "product_id": self.product_barcode.id,
                            "product_uom_qty": 20,
                            "product_uom": self.product_barcode.uom_id.id,
                            "location_id": self.supplier_location.id,
                            "location_dest_id": self.stock_location.id,
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
                            "location_id": self.supplier_location.id,
                            "location_dest_id": self.stock_location.id,
                        },
                    ),
                ],
            }
        )
        self.picking.action_confirm()
        for move_line in self.picking.move_line_ids:
            move_line.qty_done = move_line.reserved_uom_qty
        self.picking._action_done()
        for move_line_id in self.picking.move_line_ids:
            move_line_id.result_package_id = self.package
        self.wizard = (
            self.env["stock.picking.print"]
            .with_context(
                **{"active_ids": [self.picking.id], "active_model": "stock.picking"}
            )
            .create({})
        )

    def test_wizard_creation(self):
        self.wizard.barcode_report = self.env.ref(
            "stock_picking_product_barcode_report.action_label_barcode_report"
        )
        self.wizard._onchange_picking_ids()
        self.assertEqual(1, len(self.wizard.product_print_moves.ids))
        line = self.wizard.product_print_moves[0]
        self.assertEqual(line.label_qty, 1)
        self.assertEqual(line.product_id.id, self.product_barcode.id)
        # This two sentences are added just for check that not throw an exception
        self.wizard.barcode_format = "gs1_128"
        self.wizard.print_labels()
        # Check that wizard add lines with packages and the label not
        # throw an exception when trying to print it
        self.wizard.barcode_report = self.env.ref(
            "stock_picking_product_barcode_report.action_label_barcode_report_quant_package"
        )
        self.wizard._onchange_picking_ids()
        self.assertEqual(2, len(self.wizard.product_print_moves.ids))
        line = self.wizard.product_print_moves[0]
        self.assertEqual(line.label_qty, 1)
        self.assertEqual(line.product_id.id, self.product_barcode.id)
        self.wizard.print_labels()

    def test_wizard_quants(self):
        quant = self.env["stock.quant"].search(
            [("product_id", "=", self.product_barcode.id), ("quantity", ">", 0)]
        )
        quant_wizard = (
            self.env["stock.picking.print"]
            .with_context(**{"active_ids": quant.ids, "active_model": "stock.quant"})
            .create({})
        )
        quant_wizard.barcode_report = self.env.ref(
            "stock_picking_product_barcode_report.action_label_barcode_report"
        )
        self.assertEqual(len(quant_wizard.product_print_moves), 1)
        self.assertEqual(quant_wizard.product_print_moves.quantity, 20)
        quant_wizard.print_labels()
