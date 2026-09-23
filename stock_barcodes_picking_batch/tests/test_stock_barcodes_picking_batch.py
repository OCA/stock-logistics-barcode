# Copyright 2023 Sergio Teruel <sergio.teruel@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import Command
from odoo.tests.common import tagged
from odoo.tools.safe_eval import safe_eval

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
                    "move_ids": [
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
            f"Barcode reader - {self.picking_batch.name} - ",
            self.wiz_scan_picking_batch.display_name,
        )

    def test_open_actions_displays_menu(self):
        action = self.wiz_scan_picking_batch.open_actions()
        self.assertTrue(self.wiz_scan_picking_batch.display_menu)
        self.assertEqual(action["type"], "ir.actions.client")
        self.assertEqual(
            action["xml_id"], "stock_barcodes.action_stock_barcodes_action_client"
        )

    def test_picking_batch_wizard_scan_product(self):
        self._create_quant_for_product(self.stock_location, self.product_wo_tracking)
        self.picking_batch.action_assign()
        # The class-level wiz_scan_picking_batch was built in setUpClass BEFORE
        # action_assign, so its cached pending moves do not reflect the freshly
        # reserved sml. Re-build the wizard now (same pattern as the sibling
        # test_picking_batch_wizard_scan_more_product_than_needed).
        action = self.picking_batch.action_barcode_scan()
        self.wiz_scan_picking_batch = self.ScanReadPicking.browse(action["res_id"])
        # no_increase_qty_done makes each scan set qty_picked exactly to the
        # scanned qty (1 by default) instead of accumulating to the move's
        # full available_qty (a behaviour change in v18 vs v16).
        wiz_scan_picking_batch = self.wiz_scan_picking_batch.with_context(
            force_create_move=True, no_increase_qty_done=True
        )
        self.action_barcode_scanned(wiz_scan_picking_batch, "8480000723208")
        sml = self.picking_batch.move_line_ids.filtered(
            lambda x: x.product_id == self.product_wo_tracking
        )
        self.assertEqual(sum(sml.mapped("qty_picked")), 1.0)

    def test_picking_batch_wizard_scan_more_product_than_needed(self):
        self._create_quant_for_product(self.stock_location, self.product_wo_tracking)
        self.picking_batch.action_assign()

        # Modify some scan wizard behavior
        self.barcode_option_group_out.manual_entry = True
        self.barcode_option_group_out.is_manual_qty = True
        self.barcode_option_group_out.is_manual_confirm = True
        self.barcode_option_group_out.show_pending_moves = "all"

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
        self.assertEqual(sum(sml.mapped("qty_picked")), 6.0)

        # Check that all qty's have included in pickings
        self.action_barcode_scanned(wiz_scan_picking_batch, "8480000723208")
        wiz_scan_picking_batch.product_qty = 9
        wiz_scan_picking_batch.action_confirm()

        # Asserts
        sml = self.picking_batch.move_line_ids.filtered(
            lambda x: x.product_id == self.product_wo_tracking
        )
        self.assertEqual(sum(sml.mapped("qty_picked")), 15.0)

    def _create_wave_from_receptions(self):
        """Receive two pickings and put all their move lines in a wave, as a
        user does from Prepare Wave"""
        pickings = self.env["stock.picking"]
        for qty in (2, 3):
            pickings |= (
                self.env["stock.picking"]
                .with_context(planned_picking=True)
                .create(
                    {
                        "location_id": self.supplier_location.id,
                        "location_dest_id": self.stock_location.id,
                        "partner_id": self.partner_agrolite.id,
                        "picking_type_id": self.picking_type_in.id,
                        "move_ids": [
                            Command.create(
                                {
                                    "name": self.product_wo_tracking.name,
                                    "product_id": self.product_wo_tracking.id,
                                    "product_uom_qty": qty,
                                    "product_uom": self.product_wo_tracking.uom_id.id,
                                    "location_id": self.supplier_location.id,
                                    "location_dest_id": self.stock_location.id,
                                }
                            )
                        ],
                    }
                )
            )
        pickings.action_confirm()
        pickings.move_line_ids._add_to_wave()
        wave = pickings.batch_id
        self.assertTrue(wave.is_wave)
        wave.action_confirm()
        return wave

    def test_wave_reception_wizard_locations(self):
        wave = self._create_wave_from_receptions()
        action = wave.action_barcode_scan()
        wiz = self.ScanReadPicking.browse(action["res_id"])
        self.assertEqual(wiz.picking_mode, "picking_batch")
        self.assertEqual(wiz.picking_type_code, "incoming")
        self.assertEqual(wiz.picking_location_id, self.supplier_location)
        self.assertEqual(wiz.picking_location_dest_id, self.stock_location)
        self.assertEqual(wiz.company_id, wave.company_id)
        # Receptions show the destination location, not the source one
        arch = self.ScanReadPicking.get_view(
            self.env.ref(
                "stock_barcodes_picking_batch.view_stock_barcodes_read_picking_batch_form"
            ).id
        )["arch"]
        self.assertIn('name="location_dest_id"', arch)
        self.assertIn("picking_type_code == 'incoming'", arch)

    def test_wave_reception_keeps_putaway_destination(self):
        # Same as test_candidate_reuses_putaway_adjusted_line but on a wave:
        # the generic destination of the batch pickings must be known, so a
        # line routed by putaway to a sublocation is not redirected back to it.
        wave = self._create_wave_from_receptions()
        action = wave.action_barcode_scan()
        wiz = self.ScanReadPicking.browse(action["res_id"])
        moves = wave.move_ids
        moves.move_line_ids.location_dest_id = self.location_2
        wiz.location_id = self.supplier_location
        wiz.location_dest_id = self.stock_location
        wiz.product_id = self.product_wo_tracking
        self.barcode_option_group_in.show_fixed_location_dest = False
        self.assertFalse(wiz._get_candidate_stock_move_lines(moves, {}))
        self.barcode_option_group_in.show_fixed_location_dest = True
        sml_vals = {}
        candidate = wiz._get_candidate_stock_move_lines(moves, sml_vals)
        self.assertEqual(candidate, moves.move_line_ids)
        self.assertEqual(candidate.location_dest_id, self.location_2)
        self.assertNotIn("location_dest_id", sml_vals)

    def test_wave_reception_scan_redirects_to_scanned_bin(self):
        wave = self._create_wave_from_receptions()
        action = wave.action_barcode_scan()
        wiz = self.ScanReadPicking.browse(action["res_id"])
        sml = wave.move_line_ids
        # Operator chooses a destination bin, then scans the product
        wiz.location_dest_id = self.location_1
        wiz = wiz.with_context(no_increase_qty_done=True)
        self.action_barcode_scanned(wiz, self.product_wo_tracking.barcode)
        # The reserved line is reused and redirected, no new line is created
        self.assertEqual(wave.move_line_ids, sml)
        picked_sml = sml.filtered("qty_picked")
        self.assertEqual(picked_sml.location_dest_id, self.location_1)
        self.assertEqual(sum(sml.mapped("qty_picked")), 1.0)

    def test_barcode_menu_wave_action(self):
        barcode_action = self.env.ref(
            "stock_barcodes_picking_batch.stock_barcodes_action_picking_wave"
        )
        action = barcode_action.open_action()
        self.assertEqual(action["res_model"], "stock.picking.batch")
        self.assertIn(("is_wave", "=", True), safe_eval(action["domain"]))

    def _open_manual_batch_scanner(self):
        self.barcode_option_group_out.write(
            {
                "manual_entry": True,
                "is_manual_qty": True,
                "is_manual_confirm": True,
                "confirmed_moves": True,
                "show_pending_moves": "all",
            }
        )
        action = self.picking_batch.action_barcode_scan()
        wizard = self.ScanReadPicking.browse(action["res_id"])
        self.assertTrue(wizard.manual_entry)
        return wizard

    def _scan_batch_quantity(self, wizard, quantity):
        self.action_barcode_scanned(wizard, self.product_wo_tracking.barcode)
        wizard.product_qty = quantity
        wizard.action_confirm()

    def test_batch_unreserved_demand_is_split_and_validated(self):
        self._create_quant_for_product(self.stock_location, self.product_wo_tracking)
        self.assertFalse(self.picking_batch.move_line_ids)
        wizard = self._open_manual_batch_scanner()
        self.assertEqual(sum(wizard.todo_line_ids.mapped("product_uom_qty")), 6)
        self._scan_batch_quantity(wizard, 6)
        for picking in self.picking_batch.picking_ids:
            self.assertEqual(sum(picking.move_line_ids.mapped("qty_picked")), 3)
        wizard.action_validate_picking_batch()
        self.assertEqual(self.picking_batch.state, "done")
        for picking in self.picking_batch.picking_ids:
            self.assertEqual(picking.state, "done")
            self.assertEqual(sum(picking.move_line_ids.mapped("quantity")), 3)

    def test_batch_reserved_demand_is_split_and_validated(self):
        self._create_quant_for_product(self.stock_location, self.product_wo_tracking)
        self.picking_batch.action_assign()
        wizard = self._open_manual_batch_scanner()
        self._scan_batch_quantity(wizard, 6)
        self.assertEqual(wizard.total_product_uom_qty, 6)
        self.assertEqual(wizard.total_product_qty_done, 6)
        for picking in self.picking_batch.picking_ids:
            self.assertEqual(sum(picking.move_line_ids.mapped("qty_picked")), 3)
        wizard.action_validate_picking_batch()
        self.assertEqual(self.picking_batch.state, "done")
        for picking in self.picking_batch.picking_ids:
            self.assertEqual(picking.state, "done")
            self.assertEqual(sum(picking.move_line_ids.mapped("quantity")), 3)

    def test_batch_extra_quantity_is_not_duplicated(self):
        self._create_quant_for_product(self.stock_location, self.product_wo_tracking)
        wizard = self._open_manual_batch_scanner()
        self._scan_batch_quantity(wizard, 7)
        self.assertTrue(wizard.visible_force_done)
        wizard.action_force_done()
        self.assertEqual(sum(self.picking_batch.move_line_ids.mapped("qty_picked")), 7)
        self.assertEqual(
            sorted(
                sum(picking.move_line_ids.mapped("qty_picked"))
                for picking in self.picking_batch.picking_ids
            ),
            [3, 4],
        )
        wizard.action_validate_picking_batch()
        self.assertEqual(self.picking_batch.state, "done")
        self.assertEqual(sum(self.picking_batch.move_line_ids.mapped("quantity")), 7)

    def test_batch_rejects_duplicate_serial(self):
        self.product_wo_tracking.tracking = "serial"
        lot = self.env["stock.lot"].create(
            {
                "name": "BATCH-SERIAL",
                "product_id": self.product_wo_tracking.id,
                "company_id": self.env.company.id,
            }
        )
        self.env["stock.quant"]._update_available_quantity(
            self.product_wo_tracking, self.stock_location, 1, lot_id=lot
        )
        self.picking_batch.action_assign()
        wizard = self._open_manual_batch_scanner()
        for _scan in range(2):
            self.action_barcode_scanned(wizard, self.product_wo_tracking.barcode)
            self.action_barcode_scanned(wizard, lot.name)
            wizard.product_qty = 1
            wizard.action_confirm()
            self.assertEqual(
                sum(self.picking_batch.move_line_ids.mapped("qty_picked")), 1
            )

    def test_wave_reception_group_by_picking(self):
        wave = self._create_wave_from_receptions()
        self.barcode_option_group_in.group_key_for_todo_records = (
            "object.picking_id,object.product_id"
        )
        action = wave.action_barcode_scan()
        wiz = self.ScanReadPicking.browse(action["res_id"])
        # One todo line per picking, each one showing its picking reference
        self.assertEqual(len(wiz.todo_line_ids), 2)
        self.assertEqual(
            sorted(wiz.todo_line_ids.mapped("picking_names")),
            sorted(wave.picking_ids.mapped("name")),
        )

    def test_wave_reception_picking_names_default_group(self):
        wave = self._create_wave_from_receptions()
        action = wave.action_barcode_scan()
        wiz = self.ScanReadPicking.browse(action["res_id"])
        # Same location and product: both pickings are grouped in one line
        self.assertEqual(len(wiz.todo_line_ids), 1)
        self.assertEqual(
            set(wiz.todo_line_ids.picking_names.split(", ")),
            set(wave.picking_ids.mapped("name")),
        )

    def test_picking_wizard_has_no_picking_names(self):
        picking = self._create_wave_from_receptions().picking_ids[:1]
        action = picking.action_barcode_scan()
        wiz = self.ScanReadPicking.browse(action["res_id"])
        self.assertTrue(wiz.todo_line_ids)
        self.assertFalse(any(wiz.todo_line_ids.mapped("picking_names")))
