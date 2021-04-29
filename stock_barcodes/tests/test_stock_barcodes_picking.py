# Copyright 2108-2019 Sergio Teruel <sergio.teruel@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.tests.common import tagged

from odoo.addons.stock_barcodes.tests.test_stock_barcodes import TestStockBarcodes


@tagged("post_install", "-at_install")
class TestStockBarcodesPicking(TestStockBarcodes):
    def setUp(self):
        super().setUp()
        self.ScanReadPicking = self.env["wiz.stock.barcodes.read.picking"]
        self.stock_picking_model = self.env.ref("stock.model_stock_picking")

        # Model Data
        self.barcode_option_group_out = self.env.ref(
            "stock_barcodes.stock_barcodes_option_group_picking_out"
        )
        self.barcode_option_group_in = self.env.ref(
            "stock_barcodes.stock_barcodes_option_group_picking_in"
        )
        self.barcode_option_group_out.barcode_guided_mode = False
        self.barcode_option_group_in.barcode_guided_mode = False
        self.partner_agrolite = self.env.ref("base.res_partner_2")
        self.picking_type_in = self.env.ref("stock.picking_type_in")
        self.picking_type_in.barcode_option_group_id = self.barcode_option_group_in
        self.picking_type_out = self.env.ref("stock.picking_type_out")
        self.picking_type_out.barcode_option_group_id = self.barcode_option_group_out
        self.supplier_location = self.env.ref("stock.stock_location_suppliers")
        self.customer_location = self.env.ref("stock.stock_location_customers")
        self.stock_location = self.env.ref("stock.stock_location_stock")
        self.categ_unit = self.env.ref("uom.product_uom_categ_unit")
        self.categ_kgm = self.env.ref("uom.product_uom_categ_kgm")
        self.picking_out_01 = (
            self.env["stock.picking"]
            .with_context(planned_picking=True)
            .create(
                {
                    "location_id": self.stock_location.id,
                    "location_dest_id": self.customer_location.id,
                    "partner_id": self.partner_agrolite.id,
                    "picking_type_id": self.picking_type_out.id,
                    "move_lines": [
                        (
                            0,
                            0,
                            {
                                "name": self.product_tracking.name,
                                "product_id": self.product_tracking.id,
                                "product_uom_qty": 3,
                                "product_uom": self.product_tracking.uom_id.id,
                                "location_id": self.stock_location.id,
                                "location_dest_id": self.customer_location.id,
                            },
                        )
                    ],
                }
            )
        )
        self.picking_out_02 = self.picking_out_01.copy()
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
                                "name": self.product_wo_tracking.name,
                                "product_id": self.product_wo_tracking.id,
                                "product_uom_qty": 3,
                                "product_uom": self.product_wo_tracking.uom_id.id,
                                "location_id": self.supplier_location.id,
                                "location_dest_id": self.stock_location.id,
                            },
                        ),
                        (
                            0,
                            0,
                            {
                                "name": self.product_wo_tracking.name,
                                "product_id": self.product_wo_tracking.id,
                                "product_uom_qty": 5,
                                "product_uom": self.product_wo_tracking.uom_id.id,
                                "location_id": self.supplier_location.id,
                                "location_dest_id": self.stock_location.id,
                            },
                        ),
                        (
                            0,
                            0,
                            {
                                "name": self.product_tracking.name,
                                "product_id": self.product_tracking.id,
                                "product_uom_qty": 3,
                                "product_uom": self.product_tracking.uom_id.id,
                                "location_id": self.supplier_location.id,
                                "location_dest_id": self.stock_location.id,
                            },
                        ),
                        (
                            0,
                            0,
                            {
                                "name": self.product_tracking.name,
                                "product_id": self.product_tracking.id,
                                "product_uom_qty": 5,
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
        action = self.picking_in_01.action_barcode_scan()
        self.wiz_scan_picking = self.ScanReadPicking.browse(action["res_id"])

    def test_wiz_picking_values(self):
        self.picking_in_01.picking_type_id.barcode_option_group_id = self.env.ref(
            "stock_barcodes.stock_barcodes_option_group_picking_in"
        )
        self.assertEqual(
            self.wiz_scan_picking.location_id, self.picking_in_01.location_dest_id
        )
        self.assertEqual(self.wiz_scan_picking.res_model_id, self.stock_picking_model)
        self.assertEqual(self.wiz_scan_picking.res_id, self.picking_in_01.id)
        self.assertIn(
            "Barcode reader - %s - " % (self.picking_in_01.name),
            self.wiz_scan_picking.display_name,
        )

    def test_picking_wizard_scan_product(self):
        wiz_scan_picking = self.wiz_scan_picking.with_context(force_create_move=True)
        self.action_barcode_scanned(self.wiz_scan_picking, "8480000723208")
        self.assertEqual(self.wiz_scan_picking.product_id, self.product_wo_tracking)
        sml = self.picking_in_01.move_line_ids.filtered(
            lambda x: x.product_id == self.product_wo_tracking
        )
        self.assertEqual(sml.qty_done, 1.0)
        # Scan product with tracking lot enable
        self.action_barcode_scanned(self.wiz_scan_picking, "8433281006850")
        sml = self.picking_in_01.move_line_ids.filtered(
            lambda x: x.product_id == self.product_tracking
        )
        self.assertEqual(sml.qty_done, 0.0)
        self.assertEqual(
            self.wiz_scan_picking.message, "8433281006850 (Waiting lot)",
        )
        # Scan a lot. Increment quantities if scan product or other lot from
        # this product
        self.action_barcode_scanned(wiz_scan_picking, "8411822222568")
        sml = self.picking_in_01.move_line_ids.filtered(
            lambda x: x.product_id == self.product_tracking and x.lot_id
        )
        self.assertEqual(sml.lot_id, self.lot_1)
        self.assertEqual(sml.qty_done, 1.0)
        self.action_barcode_scanned(wiz_scan_picking, "8433281006850")
        stock_move = sml.move_id
        self.assertEqual(sum(stock_move.move_line_ids.mapped("qty_done")), 2.0)
        self.action_barcode_scanned(wiz_scan_picking, "8411822222568")
        self.assertEqual(sum(stock_move.move_line_ids.mapped("qty_done")), 3.0)
        self.assertEqual(
            self.wiz_scan_picking.message, "8411822222568 (OK)",
        )
        # Scan a package
        self.action_barcode_scanned(wiz_scan_picking, "5420008510489")
        # Package of 5 product units. Already three unit exists
        self.assertEqual(sum(stock_move.move_line_ids.mapped("qty_done")), 8.0)

    def test_picking_wizard_scan_product_manual_entry(self):
        wiz_scan_picking = self.wiz_scan_picking.with_context(force_create_move=True)
        self.wiz_scan_picking.manual_entry = True
        self.action_barcode_scanned(wiz_scan_picking, "8480000723208")
        self.assertEqual(wiz_scan_picking.product_id, self.product_wo_tracking)
        sml = self.picking_in_01.move_line_ids.filtered(
            lambda x: x.product_id == self.product_wo_tracking
        )
        self.assertEqual(wiz_scan_picking.product_qty, 0.0)
        self.wiz_scan_picking.product_qty = 12.0
        wiz_scan_picking.action_manual_entry()
        self.assertEqual(sml.qty_done, 8.0)
        self.assertEqual(sml.move_id.quantity_done, 12.0)

    def test_picking_wizard_remove_last_scan(self):
        self.action_barcode_scanned(self.wiz_scan_picking, "8480000723208")
        self.assertEqual(self.wiz_scan_picking.product_id, self.product_wo_tracking)
        sml = self.picking_in_01.move_line_ids.filtered(
            lambda x: x.product_id == self.product_wo_tracking
        )
        self.assertEqual(sml.qty_done, 1.0)
        self.wiz_scan_picking.action_undo_last_scan()
        self.assertEqual(sml.qty_done, 0.0)
        self.assertEqual(self.wiz_scan_picking.picking_product_qty, 0.0)

    def test_barcode_from_operation(self):
        picking_out_3 = self.picking_out_01.copy()
        self.picking_out_01.action_assign()
        self.picking_out_02.action_assign()

        action = self.picking_type_out.action_barcode_scan()
        self.wiz_scan_picking = self.ScanReadPicking.browse(action["res_id"])
        self.wiz_scan_picking.manual_entry = True
        self.wiz_scan_picking.product_id = self.product_tracking
        self.wiz_scan_picking.lot_id = self.lot_1
        self.wiz_scan_picking.product_qty = 2

        self.wiz_scan_picking.with_context(force_create_move=True).action_manual_entry()
        self.assertEqual(len(self.wiz_scan_picking.candidate_picking_ids), 2)
        # Lock first picking
        candidate = self.wiz_scan_picking.candidate_picking_ids.filtered(
            lambda c: c.picking_id == self.picking_out_01
        )
        candidate_wiz = candidate.with_context(
            wiz_barcode_id=self.wiz_scan_picking.id, picking_id=self.picking_out_01.id
        )
        candidate_wiz.with_context(force_create_move=True).action_lock_picking()
        self.assertEqual(self.picking_out_01.move_lines.quantity_done, 2)
        self.wiz_scan_picking.with_context(force_create_move=True).action_manual_entry()
        self.assertEqual(self.picking_out_01.move_lines.quantity_done, 4)

        # Picking out 3 is in confirmed state, so until confirmed moves has
        # not been activated candidate pickings is 2
        picking_out_3.action_confirm()
        candidate_wiz.action_unlock_picking()
        self.wiz_scan_picking.with_context(force_create_move=True).action_manual_entry()
        self.assertEqual(len(self.wiz_scan_picking.candidate_picking_ids), 2)
        self.wiz_scan_picking.confirmed_moves = True
        candidate_wiz.action_unlock_picking()
        self.wiz_scan_picking.with_context(force_create_move=True).action_manual_entry()
        self.assertEqual(len(self.wiz_scan_picking.candidate_picking_ids), 3)
