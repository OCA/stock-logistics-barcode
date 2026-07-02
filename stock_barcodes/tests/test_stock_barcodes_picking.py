# Copyright 2108-2019 Sergio Teruel <sergio.teruel@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from unittest import mock
from unittest.mock import call, patch

from odoo import Command, _
from odoo.exceptions import MissingError, UserError, ValidationError
from odoo.tests.common import tagged

from .common import TestCommonStockBarcodes

patch_wizard = "odoo.addons.stock_barcodes.wizard"
patch_stock_models = "odoo.addons.stock.models"
patch_manual_entry = (
    patch_wizard + ".stock_barcodes_read.WizStockBarcodesRead.action_manual_entry"
)
patch_read_picking = (
    patch_wizard + ".stock_barcodes_read_picking.WizStockBarcodesReadPicking"
)
patch_read = patch_wizard + ".stock_barcodes_read.WizStockBarcodesRead"

patch_prepare_stock_moves_domain = patch_read_picking + "._prepare_stock_moves_domain"

patch_set_messagge_info = patch_read + "._set_messagge_info"
patch_set_focus_on_qty_input = patch_read + "._set_focus_on_qty_input"
patch_check_done_conditions = patch_read + ".check_done_conditions"
patch_action_assign_serial = patch_read_picking + ".action_assign_serial"
patch_action_put_in_pack = (
    patch_stock_models + ".stock_picking.Picking.action_put_in_pack"
)


@tagged("post_install", "-at_install")
class TestStockBarcodesPicking(TestCommonStockBarcodes):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.ScanReadPicking = cls.env["wiz.stock.barcodes.read.picking"]
        cls.stock_picking_model = cls.env.ref("stock.model_stock_picking")

        # Model Data
        cls.barcode_option_group_out = cls._create_barcode_option_group_outgoing()
        cls.barcode_option_group_in = cls._create_barcode_option_group_incoming()
        cls.barcode_option_group_out_manual = cls._create_barcode_option_group_outgoing(
            manual_entry=True
        )

        cls.barcode_option_group_out.barcode_guided_mode = False
        cls.barcode_option_group_in.barcode_guided_mode = False
        cls.partner_agrolite = cls.env.ref("base.res_partner_2")
        cls.picking_type_in = cls.env.ref("stock.picking_type_in")
        cls.picking_type_in.barcode_option_group_id = cls.barcode_option_group_in
        cls.picking_type_out = cls.env.ref("stock.picking_type_out")
        cls.picking_type_out.reservation_method = "manual"
        cls.picking_type_out.barcode_option_group_id = cls.barcode_option_group_out
        cls.supplier_location = cls.env.ref("stock.stock_location_suppliers")
        cls.customer_location = cls.env.ref("stock.stock_location_customers")
        cls.stock_location = cls.env.ref("stock.stock_location_stock")
        cls.categ_unit = cls.env.ref("uom.product_uom_categ_unit")
        cls.categ_kgm = cls.env.ref("uom.product_uom_categ_kgm")
        cls.picking_out_01 = (
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
                                "name": cls.product_tracking.name,
                                "product_id": cls.product_tracking.id,
                                "product_uom_qty": 3,
                                "product_uom": cls.product_tracking.uom_id.id,
                                "location_id": cls.stock_location.id,
                                "location_dest_id": cls.customer_location.id,
                            }
                        )
                    ],
                }
            )
        )
        cls.picking_out_02 = cls.picking_out_01.copy()
        cls.picking_in_01 = (
            cls.env["stock.picking"]
            .with_context(planned_picking=True)
            .create(
                {
                    "location_id": cls.supplier_location.id,
                    "location_dest_id": cls.stock_location.id,
                    "partner_id": cls.partner_agrolite.id,
                    "picking_type_id": cls.picking_type_in.id,
                    "move_ids": [
                        Command.create(
                            {
                                "name": cls.product_wo_tracking.name,
                                "product_id": cls.product_wo_tracking.id,
                                "product_uom_qty": 3,
                                "product_uom": cls.product_wo_tracking.uom_id.id,
                                "location_id": cls.supplier_location.id,
                                "location_dest_id": cls.stock_location.id,
                            }
                        ),
                        Command.create(
                            {
                                "name": cls.product_wo_tracking.name,
                                "product_id": cls.product_wo_tracking.id,
                                "product_uom_qty": 5,
                                "product_uom": cls.product_wo_tracking.uom_id.id,
                                "location_id": cls.supplier_location.id,
                                "location_dest_id": cls.stock_location.id,
                            }
                        ),
                        Command.create(
                            {
                                "name": cls.product_tracking.name,
                                "product_id": cls.product_tracking.id,
                                "product_uom_qty": 3,
                                "product_uom": cls.product_tracking.uom_id.id,
                                "location_id": cls.supplier_location.id,
                                "location_dest_id": cls.stock_location.id,
                            }
                        ),
                        Command.create(
                            {
                                "name": cls.product_tracking.name,
                                "product_id": cls.product_tracking.id,
                                "product_uom_qty": 5,
                                "product_uom": cls.product_tracking.uom_id.id,
                                "location_id": cls.supplier_location.id,
                                "location_dest_id": cls.stock_location.id,
                            }
                        ),
                    ],
                }
            )
        )
        cls.picking_in_01.action_confirm()
        action = cls.picking_in_01.action_barcode_scan()
        cls.wiz_scan_picking = cls.ScanReadPicking.browse(action["res_id"])

        # Create a wizard for outgoing picking
        cls.picking_out_01.action_confirm()
        action = cls.picking_out_01.action_barcode_scan()
        cls.wiz_scan_picking_out = cls.ScanReadPicking.browse(action["res_id"])

    def test_incoming_scan_ignores_vendor_counterpart_qty(self):
        # On a reception, scanning a plain product must add the scanned
        # increment (+1), never the quantity of a quant. With
        # fill_fields_from_lot the scan used to read the source location (the
        # vendor location, holding the negative double-entry counterpart of
        # past receipts) and feed that negative value into the scan.
        self.barcode_option_group_in.fill_fields_from_lot = True
        # Negative counterpart quant at the vendor (source) location.
        self.env["stock.quant"]._update_available_quantity(
            self.product_wo_tracking, self.supplier_location, -8
        )
        self.assertEqual(self.wiz_scan_picking.location_id, self.supplier_location)
        wiz = self.wiz_scan_picking.with_context(force_create_move=True)
        self.action_barcode_scanned(wiz, self.product_wo_tracking.barcode)
        picked = sum(
            self.picking_in_01.move_line_ids.filtered(
                lambda x: x.product_id == self.product_wo_tracking
            ).mapped("qty_picked")
        )
        self.assertEqual(picked, 1.0)

    def test_wiz_picking_values(self):
        self.assertEqual(
            self.wiz_scan_picking.location_id, self.picking_in_01.location_id
        )
        self.assertEqual(self.wiz_scan_picking.res_model_id, self.stock_picking_model)
        self.assertEqual(self.wiz_scan_picking.res_id, self.picking_in_01.id)
        if self.wiz_scan_picking.display_name:
            self.assertIn(
                f"Barcode reader - {self.picking_in_01.name} - ",
                self.wiz_scan_picking.display_name,
            )

    def test_free_out_resolves_reserved_sublocation(self):
        # Free (non-guided) mode: scanning a product whose stock is reserved in
        # a sub-location must pick it from there, instead of failing because the
        # wizard source defaults to the picking's parent location (where the
        # product is not directly available).
        self.env["stock.quant"]._update_available_quantity(
            self.product_wo_tracking, self.location_1, 5
        )
        picking = (
            self.env["stock.picking"]
            .with_context(planned_picking=True)
            .create(
                {
                    "location_id": self.stock_location.id,
                    "location_dest_id": self.customer_location.id,
                    "partner_id": self.partner_agrolite.id,
                    "picking_type_id": self.picking_type_out.id,
                    "move_ids": [
                        Command.create(
                            {
                                "name": self.product_wo_tracking.name,
                                "product_id": self.product_wo_tracking.id,
                                "product_uom_qty": 2,
                                "product_uom": self.product_wo_tracking.uom_id.id,
                                "location_id": self.stock_location.id,
                                "location_dest_id": self.customer_location.id,
                            }
                        )
                    ],
                }
            )
        )
        picking.action_confirm()
        picking.action_assign()
        sml = picking.move_line_ids
        self.assertEqual(sml.location_id, self.location_1)
        action = picking.action_barcode_scan()
        wiz = self.ScanReadPicking.browse(action["res_id"])
        # Source defaults to the picking parent location, not the sub-location.
        self.assertEqual(wiz.location_id, self.stock_location)
        self.action_barcode_scanned(wiz, self.product_wo_tracking.barcode)
        # The scan must be applied on the reserved sub-location line.
        self.assertEqual(sml.qty_picked, 1.0)
        self.assertEqual(wiz.location_id, self.location_1)

    def test_in_redirects_dest_to_scanned_bin(self):
        # Reception: choosing a destination bin (e.g. scanning it) must
        # redirect the product to it, even when the line was already routed
        # to another sub-location (putaway).
        picking = (
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
                                "product_uom_qty": 2,
                                "product_uom": self.product_wo_tracking.uom_id.id,
                                "location_id": self.supplier_location.id,
                                "location_dest_id": self.stock_location.id,
                            }
                        )
                    ],
                }
            )
        )
        picking.action_confirm()
        picking.action_assign()
        sml = picking.move_line_ids
        # Simulate a putaway-assigned destination sub-location.
        sml.location_dest_id = self.location_1
        action = picking.action_barcode_scan()
        wiz = self.ScanReadPicking.browse(action["res_id"])
        # Operator picks a different destination bin, then scans the product.
        wiz.location_dest_id = self.location_2
        self.action_barcode_scanned(wiz, self.product_wo_tracking.barcode)
        # The reception line is redirected to the chosen bin.
        self.assertEqual(sml.location_dest_id, self.location_2)
        self.assertEqual(sml.qty_picked, 1.0)

    def test_guided_lot_name_option_does_not_crash(self):
        # A lot_name option (used to create new serials on reception) must not
        # break guided mode: determine_todo_action fills option fields from the
        # todo line, which has no lot_name field (KeyError before the fix).
        group = self.barcode_option_group_in
        group.barcode_guided_mode = "guided"
        group.option_ids.filtered(lambda o: o.field_name == "lot_id").write(
            {"field_name": "lot_name", "filled_default": True}
        )
        picking = (
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
                                "name": self.product_tracking_serial.name,
                                "product_id": self.product_tracking_serial.id,
                                "product_uom_qty": 2,
                                "product_uom": self.product_tracking_serial.uom_id.id,
                                "location_id": self.supplier_location.id,
                                "location_dest_id": self.stock_location.id,
                            }
                        )
                    ],
                }
            )
        )
        picking.action_confirm()
        picking.action_assign()
        # Opening the reader runs determine_todo_action; it must not raise.
        action = picking.action_barcode_scan()
        wiz = self.ScanReadPicking.browse(action["res_id"])
        self.assertEqual(wiz.picking_id, picking)

    def test_candidate_reuses_putaway_adjusted_line(self):
        # _get_candidate_stock_move_lines must reuse a move line routed by
        # putaway to a destination other than the picking's generic one (so a
        # scan picks into it and keeps that destination) only when
        # show_fixed_location_dest is enabled. It never recomputes putaway.
        wiz = self.wiz_scan_picking
        moves = self.picking_in_01.move_ids.filtered(
            lambda m: m.product_id == self.product_wo_tracking
        )
        # Route every move line of the product to a sublocation (fixed putaway),
        # so none matches the generic picking/wizard destination (WH/Stock).
        moves.move_line_ids.location_dest_id = self.location_2
        wiz.location_id = self.supplier_location
        wiz.location_dest_id = self.stock_location  # generic picking destination
        wiz.product_id = self.product_wo_tracking
        # Without the option the generic matching finds nothing: the lines are
        # at the sublocation, not at the picking destination.
        self.barcode_option_group_in.show_fixed_location_dest = False
        self.assertFalse(wiz._get_candidate_stock_move_lines(moves, {}))
        # With the option it reuses the putaway-adjusted lines, keeping their
        # destination (it is not overwritten in sml_vals).
        self.barcode_option_group_in.show_fixed_location_dest = True
        sml_vals = {}
        candidate = wiz._get_candidate_stock_move_lines(moves, sml_vals)
        self.assertEqual(candidate, moves.move_line_ids)
        self.assertEqual(candidate.location_dest_id, self.location_2)
        self.assertNotIn("location_dest_id", sml_vals)

    def test_picking_wizard_scan_product(self):
        # self.wiz_scan_picking.manual_entry = True
        wiz_scan_picking = self.wiz_scan_picking.with_context(
            force_create_move=True, no_increase_qty_done=True
        )
        self.action_barcode_scanned(wiz_scan_picking, "8480000723208")
        sml = self.picking_in_01.move_line_ids.filtered(
            lambda x: x.product_id == self.product_wo_tracking
        )
        self.assertEqual(sum(sml.mapped("qty_picked")), 1.0)
        # Scan product with tracking lot enable
        self.action_barcode_scanned(wiz_scan_picking, "8433281006850")
        sml = self.picking_in_01.move_line_ids.filtered(
            lambda x: x.product_id == self.product_tracking
        )
        self.assertEqual(sum(sml.mapped("qty_picked")), 0.0)
        self.assertEqual(
            self.wiz_scan_picking.message,
            "8433281006850 (Scan Product, Packaging, Lot / Serial)",
        )
        # Scan a lot. Increment quantities if scan product or other lot from
        # this product
        self.action_barcode_scanned(wiz_scan_picking, "8411822222568")
        sml = self.picking_in_01.move_line_ids.filtered(
            lambda x: x.product_id == self.product_tracking and x.lot_id
        )
        self.assertEqual(sml.lot_id, self.lot_1)
        self.assertEqual(sum(sml.mapped("qty_picked")), 1.0)
        self.action_barcode_scanned(wiz_scan_picking, "8433281006850")
        stock_move = sml.move_id
        self.assertEqual(sum(stock_move.move_line_ids.mapped("qty_picked")), 1.0)
        self.action_barcode_scanned(wiz_scan_picking, "8411822222568")
        self.assertEqual(sum(stock_move.move_line_ids.mapped("qty_picked")), 1.0)
        self.assertEqual(
            self.wiz_scan_picking.message,
            "8411822222568 (Scan Product, Packaging, Lot / Serial)",
        )
        # Scan a package
        self.action_barcode_scanned(wiz_scan_picking, "5420008510489")
        # Package of 5 product units. Already three unit exists
        self.assertEqual(sum(stock_move.move_line_ids.mapped("qty_picked")), 5.0)

    def test_picking_wizard_scan_product_manual_entry(self):
        wiz_scan_picking = self.wiz_scan_picking.with_context(
            force_create_move=True, no_increase_qty_done=True
        )
        wiz_scan_picking.manual_entry = True
        self.action_barcode_scanned(wiz_scan_picking, "8480000723208")
        sml = self.picking_in_01.move_line_ids.filtered(
            lambda x: x.product_id == self.product_wo_tracking
        )
        self.assertEqual(wiz_scan_picking.product_qty, 0.0)
        wiz_scan_picking.product_qty = 12.0
        wiz_scan_picking.action_confirm()
        self.assertEqual(sum(sml.mapped("qty_picked")), 12.0)

    def test_picking_wizard_scan_product_auto_lot(self):
        # Prepare more data
        lot_2 = self.StockProductionLot.create(
            {
                "name": "8411822222578",
                "product_id": self.product_tracking.id,
                "company_id": self.company.id,
            }
        )
        lot_3 = self.StockProductionLot.create(
            {
                "name": "8411822222588",
                "product_id": self.product_tracking.id,
                "company_id": self.company.id,
            }
        )
        quant_lot_2 = self.StockQuant.create(
            {
                "product_id": self.product_tracking.id,
                "lot_id": lot_2.id,
                "location_id": self.stock_location.id,
                "quantity": 15.0,
            }
        )
        quant_lot_3 = self.StockQuant.create(
            {
                "product_id": self.product_tracking.id,
                "lot_id": lot_3.id,
                "location_id": self.stock_location.id,
                "quantity": 10.0,
            }
        )
        self.quant_lot_1.in_date = "2021-01-01"
        quant_lot_2.in_date = "2021-01-05"
        quant_lot_3.in_date = "2021-01-06"
        # Scan product with tracking lot enable
        self.action_barcode_scanned(self.wiz_scan_picking, "8433281006850")
        self.assertEqual(
            self.wiz_scan_picking.message,
            "8433281006850 (Scan Product, Packaging, Lot / Serial)",
        )

        self.wiz_scan_picking.auto_lot = True
        # self.wiz_scan_picking.manual_entry = True

        # Removal strategy FIFO

        # No auto lot for incoming pickings
        self.action_barcode_scanned(self.wiz_scan_picking, "8433281006850")
        self.assertFalse(self.wiz_scan_picking.lot_id)

        # Continue test with a outgoing wizard
        self.wiz_scan_picking_out.option_group_id.auto_lot = True
        self.wiz_scan_picking_out.auto_lot = True
        self.action_barcode_scanned(self.wiz_scan_picking_out, "8433281006850")
        self.assertEqual(self.wiz_scan_picking_out.lot_id, self.lot_1)

        # Removal strategy LIFO
        self.wiz_scan_picking_out.lot_id = False
        self.product_tracking.categ_id.removal_strategy_id = self.env.ref(
            "stock.removal_lifo"
        )
        self.wiz_scan_picking_out.action_clean_values()
        self.action_barcode_scanned(self.wiz_scan_picking_out, "8433281006850")
        self.assertEqual(self.wiz_scan_picking_out.lot_id, lot_3)

    @classmethod
    def _create_barcode_option_group_incoming(cls):
        return cls.env["stock.barcodes.option.group"].create(
            {
                "name": "option group incoming for tests",
                "option_ids": [
                    Command.create(
                        {
                            "step": 1,
                            "name": "Location",
                            "field_name": "location_id",
                            "filled_default": True,
                            "to_scan": False,
                            "required": True,
                        }
                    ),
                    Command.create(
                        {
                            "step": 2,
                            "name": "Product",
                            "field_name": "product_id",
                            "to_scan": True,
                            "required": True,
                            "clean_after_done": True,
                        }
                    ),
                    Command.create(
                        {
                            "step": 2,
                            "name": "Packaging",
                            "field_name": "packaging_id",
                            "to_scan": True,
                            "required": False,
                        }
                    ),
                    Command.create(
                        {
                            "step": 2,
                            "name": "Lot / Serial",
                            "field_name": "lot_id",
                            "to_scan": True,
                            "required": True,
                        }
                    ),
                    Command.create(
                        {
                            "step": 3,
                            "name": "Location Dest",
                            "field_name": "location_dest_id",
                            "filled_default": True,
                            "to_scan": False,
                            "required": True,
                        }
                    ),
                    Command.create(
                        {
                            "step": 4,
                            "name": "Quantity",
                            "field_name": "product_qty",
                            "required": True,
                            "clean_after_done": True,
                        }
                    ),
                ],
            }
        )

    @classmethod
    def _create_barcode_option_group_outgoing(cls, manual_entry=False):
        return cls.env["stock.barcodes.option.group"].create(
            {
                "name": "option group outgoing for tests",
                "manual_entry": manual_entry,
                "option_ids": [
                    Command.create(
                        {
                            "step": 1,
                            "name": "Location",
                            "field_name": "location_id",
                            "to_scan": True,
                            "required": True,
                            "filled_default": True,
                        }
                    ),
                    Command.create(
                        {
                            "step": 2,
                            "name": "Product",
                            "field_name": "product_id",
                            "to_scan": True,
                            "required": True,
                        }
                    ),
                    Command.create(
                        {
                            "step": 2,
                            "name": "Packaging",
                            "field_name": "packaging_id",
                            "to_scan": True,
                            "required": False,
                        }
                    ),
                    Command.create(
                        {
                            "step": 2,
                            "name": "Lot / Serial",
                            "field_name": "lot_id",
                            "to_scan": True,
                            "required": True,
                        }
                    ),
                    Command.create(
                        {
                            "step": 3,
                            "name": "Location Dest",
                            "field_name": "location_dest_id",
                            "filled_default": True,
                            "to_scan": False,
                            "required": True,
                        }
                    ),
                    Command.create(
                        {
                            "step": 4,
                            "name": "Quantity",
                            "field_name": "product_qty",
                            "required": True,
                            "clean_after_done": True,
                        }
                    ),
                ],
            }
        )

    def test_stock_picking_validate(self):
        self.picking_in_01.state = False
        with self.assertRaises(UserError):
            self.picking_in_01.with_context(
                stock_barcodes_validate_picking=True
            ).button_validate()

    def test_barcode_read_picking(self):
        self.picking_in_01.state = "done"
        self.wiz_scan_picking._compute_enable_add_product()
        self.assertFalse(self.wiz_scan_picking.enable_add_product)

        self.wiz_scan_picking.show_detailed_operations = False
        self.wiz_scan_picking.action_show_detailed_operations()
        self.assertTrue(self.wiz_scan_picking.action_show_detailed_operations)

        self.wiz_scan_picking.action_show_detailed_operations()
        self.assertFalse(self.wiz_scan_picking.show_detailed_operations)

    def test_barcode_read_inventory(self):
        context = {
            "params": {
                "model": "wiz.stock.barcodes.read.inventory",
                "id": self.quant_lot_1.id,
            }
        }
        with self.assertRaises(MissingError):
            self.quant_lot_1.with_context(
                **context
            ).action_barcode_inventory_quant_unlink()
        context = {
            "params": {
                "model": self.wiz_scan_read_inventory._name,
                "id": self.wiz_scan_read_inventory.id,
            }
        }
        self.quant_lot_1.with_context(**context).action_barcode_inventory_quant_unlink()
        self.assertIsNone(
            self.quant_lot_1.with_context(
                **context
            ).action_barcode_inventory_quant_unlink()
        )
        self.assertIsNone(self.quant_lot_1.enable_current_operations())
        self.assertIsNone(self.quant_lot_1.action_barcode_inventory_quant_edit())
        with self.assertRaises(ValueError):
            self.quant_lot_1.write({"inventory_quantity": "test"})
            self.quant_lot_1.operation_quantities_rest()
            self.quant_lot_1.operation_quantities()
        self.assertEqual(
            type(self.picking_in_01.picking_type_id.get_action_picking_tree_ready()),
            dict,
        )
        self.assertEqual(
            type(
                self.picking_in_01.picking_type_id.with_context(
                    **{"operations_mode": True}
                ).get_action_picking_tree_ready()
            ),
            dict,
        )

    def test_onchange_picking_id(self):
        with (
            patch.object(type(self.wiz_scan), "fill_pending_moves"),
            patch.object(type(self.wiz_scan), "determine_todo_action") as mock_msg,
        ):
            self.wiz_scan.onchange_picking_id()
            mock_msg.assert_called_once()

    def test_determine_todo_action(self):
        result = self.wiz_scan.determine_todo_action()
        self.assertFalse(result)

        with (
            patch.object(type(self.wiz_scan), "update_fields_after_determine_todo"),
            patch.object(type(self.wiz_scan), "action_show_step") as mock_msg,
        ):
            self.wiz_scan_option_guided.determine_todo_action()
            self.assertEqual(
                self.wiz_scan_option_guided.location_id,
                self.wiz_scan_option_guided.todo_line_id.location_id,
            )

            self.wiz_scan_option_guided.picking_type_code = "outgoing"
            self.wiz_scan_option_guided.option_group_id = self.option_group2.id
            self.wiz_scan_option_guided.determine_todo_action()
            self.assertFalse(self.wiz_scan_option_guided.location_id)

            self.wiz_scan_option_guided.option_group_id = self.option_group4.id
            self.wiz_scan_option_guided.determine_todo_action()
            self.assertEqual(
                self.wiz_scan_option_guided.location_dest_id,
                self.wiz_scan_option_guided.todo_line_id.location_dest_id,
            )

            self.wiz_scan_option_guided.picking_type_code = "outgoing"
            self.wiz_scan_option_guided.option_group_id = self.option_group2.id
            self.wiz_scan_option_guided.determine_todo_action()
            self.assertFalse(self.wiz_scan_option_guided.location_dest_id)

            self.wiz_scan_option_guided.option_group_id = self.option_group7.id
            self.wiz_scan_option_guided.determine_todo_action()
            self.assertEqual(
                self.wiz_scan_option_guided.package_id,
                self.wiz_scan_option_guided.todo_line_id.package_id,
            )

            self.assertEqual(mock_msg.call_count, 2)

    def test_check_guided_restrictions(self):
        result = self.wiz_scan_option_guided._check_guided_restrictions()
        self.assertTrue(result)

        with patch.object(
            type(self.wiz_scan_option_guided), "_set_messagge_info"
        ) as mock_msg:
            self.wiz_scan_option_guided.product_id = self.product_tracking.id
            self.wiz_scan_option_guided.option_group_id = self.option_group8.id
            result = self.wiz_scan_option_guided._check_guided_restrictions()
            self.assertFalse(result)
            mock_msg.assert_called_once_with("more_match", _("Wrong product"))

    def test_action_assign_serial_required_hook_key(self):
        with self.assertRaises(ValidationError):
            self.wiz_scan.action_assign_serial()

        with (
            patch.object(type(self.StockMove), "action_assign_serial"),
            patch.object(
                type(self.wiz_scan),
                "_prepare_stock_moves_domain",
                return_value=[("id", "in", [self.stock_move_test.id])],
            ) as mock_msg,
        ):
            self.wiz_scan.product_id = self.product_tracking.id
            self.wiz_scan.action_assign_serial()
            mock_msg.assert_called_once()

        with patch.object(type(self.wiz_scan), "_option_required_hook") as mock_msg:
            self.wiz_scan._option_required_hook(option_required=self.option_group1)
            mock_msg.assert_called_once()

        with patch.object(
            type(self.StockLocation),
            "_get_putaway_strategy",
            return_value=self.location_1,
        ) as mock_msg:
            self.wiz_scan.option_group_id = self.option_group9.id
            self.wiz_scan.picking_id = self.picking_in_01.id
            result = self.wiz_scan._option_required_hook(
                option_required=self.option_group9.option_ids[0]
            )
            self.assertTrue(result)
            mock_msg.assert_called_once()

        result = self.wiz_scan._group_key(line=self.wiz_scan.todo_line_id)
        self.assertIsInstance(result, tuple)

    def test_action_open_picking(self):
        action = self.wiz_scan_picking.action_open_picking()
        self.assertEqual(action["res_model"], "stock.picking")
        self.assertEqual(action["res_id"], self.picking_in_01.id)

    def test_action_validate_picking(self):
        with patch.object(
            type(self.StockPicking), "button_validate", return_value=True
        ) as mock_validate:
            result = self.wiz_scan_picking.action_validate_picking()
            mock_validate.assert_called_once()
            # When button_validate returns True the action after validate is returned
            self.assertEqual(result.get("type"), "ir.actions.act_window")

    def test_get_stock_move_lines_todo(self):
        self.wiz_scan.picking_id = self.picking.id
        move_lines = self.wiz_scan._get_stock_move_lines_todo()
        self.assertTrue(len(move_lines) > 0)

    def test_get_moves_or_move_lines(self):
        self.wiz_scan.option_group_id = self.option_group10.id
        move_lines = self.wiz_scan.get_moves_or_move_lines()
        self.assertIsInstance(move_lines, type(self.StockMoveLine))

        self.wiz_scan.option_group_id = self.option_group9.id
        move_ids = self.wiz_scan.get_moves_or_move_lines()
        self.assertIsInstance(move_ids, type(self.StockMove))

    @mock.patch(patch_read_picking + ".action_done")
    @mock.patch(patch_manual_entry)
    def test_action_manual_entry(self, mock_manual_entry, mock_action_done):
        mock_manual_entry.return_value = True
        result = self.WizScanReadPicking.action_manual_entry()
        self.assertTrue(result)
        mock_action_done.assert_called_once()
        mock_manual_entry.assert_called_once()

    def test_create_new_stock_move(self):
        self.WizScanReadPicking.create_new_stock_move(self.test_move_line)
        self.assertTrue(self.test_move_line.move_id)

        self.wiz_scan_option_guided.todo_line_id = self.wiz_scan_read_todo.id
        self.wiz_scan_option_guided._compute_todo_line_display_ids()
        self.assertEqual(
            self.wiz_scan_option_guided.todo_line_display_ids, self.wiz_scan_read_todo
        )
        with self.assertRaises(ValidationError):
            self.wiz_scan_option_guided.with_context(
                picking=False
            )._prepare_move_line_values(None, None)

        self.wiz_scan_option_guided.owner_id = self.test_partner_id.id
        result = self.wiz_scan_option_guided.with_context(
            picking=self.picking_in_01
        )._prepare_move_line_values(self.test_move_line.move_id, 10)
        self.assertIsInstance(result, dict)
        self.assertIn("owner_id", result)
        self.assertEqual(result.get("owner_id", False), self.test_partner_id.id)

    def test_update_keep_values(self):
        keep_vals = {
            "location_dest_id": self.location_1.id,
        }
        self.wiz_scan_option_guided.option_group_id = self.option_group9.id
        self.wiz_scan_option_guided.update_keep_values(keep_vals)
        self.assertEqual(
            self.wiz_scan_option_guided.location_dest_id.name, self.location_1.name
        )

    def test_get_candidate_line_domain(self):
        self.wiz_scan_option_guided.product_id = self.product_wo_tracking.id
        self.wiz_scan_option_guided.product_qty = 100
        self.wiz_scan_option_guided.package_id = self.quant_package_1.id
        result = self.wiz_scan_option_guided.with_user(
            self.user_test_lot
        )._get_candidate_line_domain()
        self.assertTrue(len(result) > 0)
        self.assertEqual(
            self.wiz_scan_option_guided.result_package_id, self.quant_package_1
        )

    @mock.patch(patch_set_focus_on_qty_input)
    @mock.patch(patch_set_messagge_info)
    def test_check_done_conditions(
        self, mock_set_messagge_info, mock_set_focus_on_qty_input
    ):
        self.wiz_scan_option_guided.product_id = self.product_wo_tracking.id
        self.wiz_scan_option_guided.product_qty = 100
        self.wiz_scan_option_guided.qty_available = 100
        self.wiz_scan_option_guided.option_group_id = self.option_group10.id
        self.wiz_scan_option_guided.picking_type_code = "outgoing"
        result = self.wiz_scan_option_guided.with_context(
            force_create_move=False
        ).check_done_conditions()
        self.assertFalse(result)
        self.wiz_scan_option_guided.picking_type_code = "incoming"
        self.wiz_scan_option_guided.picking_id = self.picking_in_01.id
        result = self.wiz_scan_option_guided.check_done_conditions()
        self.assertFalse(result)
        self.assertEqual(mock_set_messagge_info.call_count, 4)
        # The scanned product is not part of the picking demand, so the picking
        # override rejects it right after the base "Waiting location" message.
        expected_calls = [
            call("info", "Waiting location"),
            call("not_found", "Product not demanded"),
            call("info", "Waiting location"),
            call("not_found", "Product not demanded"),
        ]
        mock_set_messagge_info.assert_has_calls(expected_calls)
        mock_set_focus_on_qty_input.assert_not_called()

    def test_update_fields_after_determine_todo(self):
        self.wiz_scan_option_guided.update_fields_after_determine_todo(
            self.wiz_scan_read_todo
        )
        self.assertEqual(
            self.wiz_scan_option_guided.picking_product_qty,
            self.wiz_scan_read_todo.qty_done,
        )

    @mock.patch(patch_action_put_in_pack)
    def test_action_put_in_pack(self, mock_action_put_in_pack):
        self.wiz_scan_option_guided.picking_id = self.picking_in_01.id
        self.wiz_scan_option_guided.action_put_in_pack()
        mock_action_put_in_pack.assert_called_once()

    @mock.patch(patch_action_assign_serial)
    @mock.patch(patch_prepare_stock_moves_domain)
    def test_action_assign_serial(
        self, mock_prepare_stock_moves_domain, mock_action_assign_serial
    ):
        mock_prepare_stock_moves_domain._prepare_stock_moves_domain.return_value = [
            ("id", "in", [self.stock_move_assigned.id, self.stock_move_test.id])
        ]
        self.wiz_scan_option_guided.action_assign_serial()
        mock_action_assign_serial.assert_called_once()

    def test_group_key(self):
        result = self.wiz_scan_option_guided._group_key(self.test_move_line)
        self.assertEqual(result[0], self.stock_location.id)
        self.assertEqual(result[1], self.product_tracking.id)

        self.option_group10.group_key_for_todo_records = "2 + 2"
        self.wiz_scan_option_guided.option_group_id = self.option_group10.id
        result = self.wiz_scan_option_guided._group_key(self.test_move_line)
        self.assertEqual(result, 4)

    def test_update_fill_record_values(self):
        vals = {
            "is_stock_move_line_origin": False,
            "product_uom_qty": 0,
            "product_qty_reserved": 0,
            "line_ids": [(0, 1, [self.test_move_line1.id])],
            "stock_move_ids": [(0, 1, [self.stock_move_assigned1.id])],
        }
        result = self.wiz_scan_option_guided._update_fill_record_values(
            self.stock_move_assigned1, vals
        )
        self.assertIsInstance(result, dict)
        # For move based todo records the scanned move is appended to stock_move_ids
        self.assertIn(self.stock_move_assigned1.id, result["stock_move_ids"][0][2])
        vals.update(
            {
                "is_stock_move_line_origin": True,
            }
        )
        result = self.wiz_scan_option_guided._update_fill_record_values(
            self.test_move_line, vals
        )
        self.assertIsInstance(result, dict)

    def test_compute_pending_move_ids(self):
        wiz = self.wiz_scan_picking
        self.assertTrue(wiz.todo_line_ids)
        wiz.option_group_id.show_pending_moves = "none"
        wiz._compute_pending_move_ids()
        self.assertFalse(wiz.pending_move_ids)
        wiz.option_group_id.show_pending_moves = "all"
        wiz._compute_pending_move_ids()
        self.assertEqual(
            wiz.pending_move_ids,
            wiz.todo_line_ids.filtered(lambda t: not t.is_extra_line),
        )
        wiz.option_group_id.show_pending_moves = "pending"
        wiz._compute_pending_move_ids()
        self.assertTrue(all(t.state == "pending" for t in wiz.pending_move_ids))

    def test_guided_all_advances_past_done_group(self):
        # show_pending_moves="all" also lists DONE lines in the pending kanban.
        # The guided next-todo selection (grouped/forced-key path) must still
        # skip done lines: after completing a grouped todo the reader must
        # advance to the next pending group, not stay on the finished one.
        group = self.barcode_option_group_in
        group.barcode_guided_mode = "guided"
        group.show_pending_moves = "all"
        group.group_key_for_todo_records = "object.product_id.id"
        wiz = self.wiz_scan_picking
        wiz.fill_todo_records()
        wiz.determine_todo_action()
        done_group = wiz.todo_line_id
        self.assertTrue(done_group)
        done_product = done_group.product_id
        # Complete every move line of this group so its todo line is "done".
        for sml in done_group.line_ids:
            sml.qty_picked = sml.quantity
        # The refresh that runs after a scan keeps the finished group as the
        # forced key; guided must not re-select it, it must move on.
        wiz.forced_todo_key = str(wiz._group_key(done_group))
        wiz.refresh_todo_records()
        self.assertTrue(wiz.todo_line_id)
        self.assertEqual(wiz.todo_line_id.state, "pending")
        self.assertNotEqual(wiz.todo_line_id.product_id, done_product)

    def test_allow_not_demanded_product(self):
        # When allow_not_demanded_product is enabled the "Product not demanded"
        # message is not raised for products outside the picking demand.
        wiz = self.wiz_scan_option_guided
        wiz.option_group_id = self.option_group10
        wiz.option_group_id.allow_not_demanded_product = True
        wiz.product_id = self.product_wo_tracking.id
        wiz.product_qty = 1
        with patch.object(type(wiz), "_set_messagge_info") as mock_msg:
            wiz.check_done_conditions()
            messages = [args[1] for args, _kw in mock_msg.call_args_list]
            self.assertNotIn("Product not demanded", messages)

    def test_search_picking_from_product(self):
        wiz = self.ScanReadPicking.create(
            {
                "option_group_id": self.barcode_option_group_in.id,
                "step": 1,
                "picking_type_code": "incoming",
            }
        )
        wiz.option_group_id.search_picking_from_product = "first"
        wiz.product_id = self.product_wo_tracking.id
        action = wiz.action_picking_from_product()
        self.assertTrue(action)
        self.assertEqual(wiz.picking_id, self.picking_in_01)

    def test_auto_put_in_pack(self):
        # When auto_put_in_pack is enabled, validating a picking without result
        # package triggers action_put_in_pack before the standard validation.
        self.picking_type_in.barcode_option_group_id.auto_put_in_pack = True
        with (
            patch.object(
                type(self.StockPicking), "action_put_in_pack"
            ) as mock_put_in_pack,
            patch(
                "odoo.addons.stock.models.stock_picking.Picking.button_validate",
                return_value=True,
            ),
        ):
            self.picking_in_01.button_validate()
            mock_put_in_pack.assert_called_once()

    def test_keep_screen_values(self):
        # With keep_screen_values, refreshing the todo records while the current
        # line is still pending must not clean the screen values.
        wiz = self.wiz_scan_picking
        wiz.todo_line_id = wiz.todo_line_ids.filtered(lambda t: t.state == "pending")[
            :1
        ]
        self.assertTrue(wiz.todo_line_id)
        with (
            patch.object(type(wiz), "fill_todo_records"),
            patch.object(type(wiz), "determine_todo_action"),
            patch.object(type(wiz), "action_show_step"),
            patch.object(type(wiz), "update_keep_values"),
        ):
            wiz.option_group_id.keep_screen_values = True
            with patch.object(type(wiz), "action_clean_values") as mock_clean:
                wiz.refresh_todo_records()
                mock_clean.assert_not_called()
            wiz.option_group_id.keep_screen_values = False
            with patch.object(type(wiz), "action_clean_values") as mock_clean:
                wiz.refresh_todo_records()
                mock_clean.assert_called_once()
