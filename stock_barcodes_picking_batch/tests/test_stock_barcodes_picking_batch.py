# Copyright 2023 Sergio Teruel <sergio.teruel@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import Command
from odoo.tests.common import tagged

from odoo.addons.stock_barcodes.tests.test_stock_barcodes_picking import (
    TestStockBarcodesPicking,
)


@tagged("post_install", "-at_install")
class TestStockBarcodesPickingBatch(TestStockBarcodesPicking):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(
            context=dict(
                cls.env.context,
                mail_create_nolog=True,
                mail_create_nosubscribe=True,
                mail_notrack=True,
                no_reset_password=True,
                tracking_disable=True,
            )
        )
        cls.ScanReadPicking = cls.env["wiz.stock.barcodes.read.picking"]
        cls.stock_picking_model = cls.env.ref("stock.model_stock_picking")
        cls.stock_picking_batch_model = cls.env.ref(
            "stock_picking_batch.model_stock_picking_batch"
        )

        # Model Data
        cls.barcode_option_group_out = cls._create_barcode_option_group_outgoing()
        cls.barcode_option_group_out.barcode_guided_mode = False

        cls.partner_agrolite = cls.env.ref("base.res_partner_2")
        cls.partner_gemini = cls.env.ref("base.res_partner_3")
        cls.picking_type_out = cls.env.ref("stock.picking_type_out")
        cls.picking_type_out.reservation_method = "manual"
        cls.picking_type_out.barcode_option_group_id = cls.barcode_option_group_out
        cls.customer_location = cls.env.ref("stock.stock_location_customers")
        cls.stock_location = cls.env.ref("stock.stock_location_stock")
        cls.picking_out1_bp = (
            cls.env["stock.picking"]
            .with_context(planned_picking=True)
            .create(
                {
                    "location_id": cls.stock_location.id,
                    "location_dest_id": cls.customer_location.id,
                    "partner_id": cls.partner_agrolite.id,
                    "picking_type_id": cls.picking_type_out.id,
                    "move_lines": [
                        Command.create(
                            {
                                "name": cls.product_wo_tracking.name,
                                "product_id": cls.product_wo_tracking.id,
                                "product_uom_qty": 3,
                                "product_uom": cls.product_wo_tracking.uom_id.id,
                                "location_id": cls.stock_location.id,
                                "location_dest_id": cls.customer_location.id,
                            }
                        )
                    ],
                }
            )
        )
        cls.picking_out2_bp = cls.picking_out1_bp.copy()

        # Create a wizard for outgoing picking
        cls.picking_out1_bp.action_confirm()
        cls.picking_out2_bp.partner_id = cls.partner_gemini
        cls.picking_out2_bp.action_confirm()

        # Create a batch picking with picking1 and picking 2
        cls.picking_batch = cls.env["stock.picking.batch"].create(
            {"name": "picking batch for test"}
        )
        cls.picking_out1_bp.batch_id = cls.picking_batch
        cls.picking_out2_bp.batch_id = cls.picking_batch
        cls.picking_batch.action_confirm()

        action = cls.picking_batch.action_barcode_scan()
        cls.wiz_scan_picking_batch = cls.ScanReadPicking.browse(action["res_id"])

    @classmethod
    def _create_quant_for_product(cls, location, product, qty=100.00):
        cls.env["stock.quant"].create(
            {
                "product_id": product.id,
                "location_id": location.id,
                "quantity": qty,
            }
        )

    def test_wiz_scan_picking_batch_values(self):
        self.assertEqual(
            self.wiz_scan_picking_batch.location_id, self.picking_out_01.location_id
        )
        self.assertEqual(
            self.wiz_scan_picking_batch.res_model_id, self.stock_picking_batch_model
        )
        self.assertEqual(self.wiz_scan_picking_batch.res_id, self.picking_batch.id)
        self.assertIn(
            "Barcode reader - %s - " % (self.picking_batch.name),
            self.wiz_scan_picking_batch.display_name,
        )

    def test_picking_batch_wizard_scan_product(self):
        self._create_quant_for_product(self.stock_location, self.product_wo_tracking)
        self.picking_batch.action_assign()
        wiz_scan_picking_batch = self.wiz_scan_picking_batch.with_context(
            force_create_move=True
        )
        self.action_barcode_scanned(wiz_scan_picking_batch, "8480000723208")
        sml = self.picking_batch.move_line_ids.filtered(
            lambda x: x.product_id == self.product_wo_tracking
        )
        self.assertEqual(sum(sml.mapped("qty_done")), 1.0)

    def test_picking_batch_wizard_scan_more_product_than_needed(self):
        self._create_quant_for_product(self.stock_location, self.product_wo_tracking)
        self.picking_batch.action_assign()

        # Modify some scan wizard behavior
        self.barcode_option_group_out.manual_entry = True
        self.barcode_option_group_out.is_manual_qty = True
        self.barcode_option_group_out.is_manual_confirm = True
        self.barcode_option_group_out.show_pending_moves = True

        action = self.picking_batch.action_barcode_scan()
        self.wiz_scan_picking_batch = self.ScanReadPicking.browse(action["res_id"])
        wiz_scan_picking_batch = self.wiz_scan_picking_batch.with_context(
            force_create_move=True
        )
        self.action_barcode_scanned(wiz_scan_picking_batch, "8480000723208")
        wiz_scan_picking_batch.product_qty = 6
        wiz_scan_picking_batch.action_confirm()

        # Asserts
        sml = self.picking_batch.move_line_ids.filtered(
            lambda x: x.product_id == self.product_wo_tracking
        )
        self.assertEqual(sum(sml.mapped("qty_done")), 6.0)

        # Check that all qty's have included in pickings
        self.action_barcode_scanned(wiz_scan_picking_batch, "8480000723208")
        wiz_scan_picking_batch.product_qty = 9
        wiz_scan_picking_batch.action_confirm()

        # Asserts
        sml = self.picking_batch.move_line_ids.filtered(
            lambda x: x.product_id == self.product_wo_tracking
        )
        self.assertEqual(sum(sml.mapped("qty_done")), 15.0)
