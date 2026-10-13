# Copyright 2026 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import Command
from odoo.tests import tagged

from .common import TestCommonStockBarcodes
from .test_scan_uom import ScanUomCommon


@tagged("post_install", "-at_install")
class TestScanAllocation(ScanUomCommon):
    def _sibling_picking(self, demand=2, uom=None):
        picking, _wizard = self._scan_picking(
            self.product_wo_tracking, demand, uom or self.unit
        )
        first_move = picking.move_ids
        second_move = first_move.copy(
            {
                "product_uom_qty": 1,
                "product_uom": self.unit.id,
                "move_line_ids": [],
                "state": "draft",
            }
        )
        second_move._action_confirm(merge=False)
        return picking, first_move, second_move

    def _scan_and_validate(self, picking, quantity):
        action = picking.action_barcode_scan(option_group=self.scan_options)
        wizard = self.WizScanReadPicking.browse(action["res_id"])
        wizard.manual_entry = True
        self.action_barcode_scanned(wizard, self.product_wo_tracking.barcode)
        wizard.product_qty = quantity
        wizard.action_confirm()
        wizard.action_validate_picking()
        self.assertEqual(picking.state, "done")
        self.assertEqual(
            sum(picking.move_line_ids.mapped("quantity_product_uom")), quantity
        )

    def test_allocate_unreserved_sibling_demand(self):
        picking, first_move, second_move = self._sibling_picking()
        picking.do_unreserve()
        self._scan_and_validate(picking, 3)
        self.assertEqual(first_move.quantity, 2)
        self.assertEqual(second_move.quantity, 1)

    def test_allocate_existing_line_before_unreserved_sibling(self):
        picking, first_move, second_move = self._sibling_picking()
        picking.do_unreserve()
        self.env["stock.move.line"].create(
            {
                "move_id": first_move.id,
                "picking_id": picking.id,
                "product_id": self.product_wo_tracking.id,
                "product_uom_id": self.unit.id,
                "quantity": 2,
                "location_id": picking.location_id.id,
                "location_dest_id": picking.location_dest_id.id,
            }
        )
        self._scan_and_validate(picking, 3)
        self.assertEqual(first_move.quantity, 2)
        self.assertEqual(second_move.quantity, 1)

    def test_allocate_siblings_with_different_uoms(self):
        picking, first_move, second_move = self._sibling_picking(1, self.dozen)
        picking.do_unreserve()
        self._scan_and_validate(picking, 13)
        self.assertEqual(first_move.quantity, 1)
        self.assertEqual(second_move.quantity, 1)


@tagged("post_install", "-at_install")
class TestScanSiblingMoves(TestCommonStockBarcodes):
    """Outgoing pickings with several moves of the same product (e.g. sale
    orders merged in one picking): reads must honor each move's demand."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.picking_type_out = cls.env.ref("stock.picking_type_out")
        cls.customer_location = cls.env.ref("stock.stock_location_customers")
        # fill_fields_from_lot + clean_after_done allow chaining serial reads
        cls.mm_option_group = cls.StockBarcodesOptionGroup.create(
            {
                "name": "Multi-move OUT options",
                "show_pending_moves": "pending",
                "source_pending_moves": "move_line_ids",
                "confirmed_moves": True,
                "fill_fields_from_lot": True,
                "option_ids": [
                    Command.create(
                        {
                            "step": 1,
                            "name": "Product",
                            "field_name": "product_id",
                            "to_scan": True,
                            "required": True,
                            "clean_after_done": True,
                        }
                    ),
                    Command.create(
                        {
                            "step": 1,
                            "name": "Lot / Serial",
                            "field_name": "lot_id",
                            "to_scan": True,
                            "required": True,
                            "clean_after_done": True,
                        }
                    ),
                    Command.create(
                        {
                            "step": 2,
                            "name": "Location",
                            "field_name": "location_id",
                            "to_scan": False,
                            "required": True,
                            "clean_after_done": True,
                        }
                    ),
                    Command.create(
                        {
                            "step": 3,
                            "name": "Quantity",
                            "field_name": "product_qty",
                            "to_scan": False,
                            "required": True,
                            "clean_after_done": True,
                        }
                    ),
                ],
            }
        )

    def _add_serial(self, product, name):
        lot = self.StockProductionLot.create(
            {
                "name": name,
                "product_id": product.id,
                "company_id": self.company.id,
            }
        )
        self.StockQuant.create(
            {
                "product_id": product.id,
                "lot_id": lot.id,
                "location_id": self.stock_location.id,
                "quantity": 1,
            }
        )
        return lot

    def _create_multi_move_picking(self, product, demands):
        # Distinct description_picking prevents merging the sibling moves
        picking = self.StockPicking.create(
            {
                "picking_type_id": self.picking_type_out.id,
                "location_id": self.stock_location.id,
                "location_dest_id": self.customer_location.id,
                "move_ids": [
                    Command.create(
                        {
                            "name": product.name,
                            "description_picking": f"order line {index}",
                            "product_id": product.id,
                            "product_uom_qty": demand,
                            "product_uom": product.uom_id.id,
                            "location_id": self.stock_location.id,
                            "location_dest_id": self.customer_location.id,
                        }
                    )
                    for index, demand in enumerate(demands)
                ],
            }
        )
        picking.action_confirm()
        return picking

    def _open_wizard(self, picking):
        action = picking.action_barcode_scan(option_group=self.mm_option_group)
        return self.WizScanReadPicking.browse(action["res_id"])

    def _scan_unit(self, wiz, product, lot_name=None):
        self.action_barcode_scanned(wiz, lot_name or product.barcode)

    def _picked(self, move):
        return sum(move.move_line_ids.mapped("qty_picked"))

    def _get_sibling_moves(self, picking, product):
        moves = picking.move_ids.filtered(lambda sm: sm.product_id == product)
        return (
            moves.filtered(lambda sm: sm.product_uom_qty == 2),
            moves.filtered(lambda sm: sm.product_uom_qty == 1),
        )

    def test_extra_read_goes_to_unreserved_sibling(self):
        """A read of a non reserved serial fills the unreserved sibling."""
        product = self.product_tracking_serial
        self._add_serial(product, "MM-S1")
        self._add_serial(product, "MM-S2")
        picking = self._create_multi_move_picking(product, [2, 1])
        picking.action_assign()
        move_a, move_b = self._get_sibling_moves(picking, product)
        self.assertEqual(len(move_a.move_line_ids), 2)
        self.assertFalse(move_b.move_line_ids)
        self._add_serial(product, "MM-S3")
        wiz = self._open_wizard(picking)
        self._scan_unit(wiz, product, "MM-S1")
        self._scan_unit(wiz, product, "MM-S2")
        self._scan_unit(wiz, product, "MM-S3")
        self.assertEqual(self._picked(move_a), 2)
        self.assertEqual(self._picked(move_b), 1)
        self.assertNotIn("higher than necessary", wiz.message)
        self.assertFalse(wiz.visible_force_done)
        picking.with_context(
            stock_barcodes_read_picking_id=wiz.id,
            button_validate_picking_ids=picking.ids,
        ).button_validate()
        self.assertEqual(picking.state, "done")
        self.assertFalse(self.StockPicking.search([("backorder_id", "=", picking.id)]))
        self.assertEqual(move_a.quantity, 2)
        self.assertEqual(move_b.quantity, 1)

    def test_reserved_sibling_keeps_receiving_extra_reads(self):
        """With the sibling reserved the unmatched read is assigned to it."""
        product = self.product_tracking_serial
        for name in ("MM-R1", "MM-R2", "MM-R3"):
            self._add_serial(product, name)
        picking = self._create_multi_move_picking(product, [2, 1])
        picking.action_assign()
        move_a, move_b = self._get_sibling_moves(picking, product)
        self.assertEqual(len(move_b.move_line_ids), 1)
        self._add_serial(product, "MM-R4")
        wiz = self._open_wizard(picking)
        self._scan_unit(wiz, product, "MM-R1")
        self._scan_unit(wiz, product, "MM-R2")
        self._scan_unit(wiz, product, "MM-R4")
        self.assertEqual(self._picked(move_a), 2)
        self.assertEqual(self._picked(move_b), 1)

    def test_real_excess_still_warns_and_is_forceable(self):
        """A read over the total demand warns and can be forced."""
        product = self.product_tracking_serial
        self._add_serial(product, "MM-E1")
        self._add_serial(product, "MM-E2")
        picking = self._create_multi_move_picking(product, [2, 1])
        picking.action_assign()
        move_a, move_b = self._get_sibling_moves(picking, product)
        self._add_serial(product, "MM-E3")
        self._add_serial(product, "MM-E4")
        wiz = self._open_wizard(picking)
        self._scan_unit(wiz, product, "MM-E1")
        self._scan_unit(wiz, product, "MM-E2")
        self._scan_unit(wiz, product, "MM-E3")
        self._scan_unit(wiz, product, "MM-E4")
        self.assertIn("higher than necessary", wiz.message)
        self.assertTrue(wiz.visible_force_done)
        self.assertEqual(self._picked(move_a), 2)
        self.assertEqual(self._picked(move_b), 1)
        wiz.action_force_done()
        self.assertEqual(self._picked(move_a), 3)
        self.assertEqual(self._picked(move_b), 1)

    def test_cancelled_sibling_is_not_pending_demand(self):
        """A cancelled sibling neither absorbs reads nor counts as demand."""
        product = self.product_tracking_serial
        self._add_serial(product, "MM-C1")
        self._add_serial(product, "MM-C2")
        picking = self._create_multi_move_picking(product, [2, 1])
        picking.action_assign()
        move_a, move_b = self._get_sibling_moves(picking, product)
        move_b._action_cancel()
        self._add_serial(product, "MM-C3")
        wiz = self._open_wizard(picking)
        self._scan_unit(wiz, product, "MM-C1")
        self._scan_unit(wiz, product, "MM-C2")
        self._scan_unit(wiz, product, "MM-C3")
        self.assertIn("higher than necessary", wiz.message)
        self.assertTrue(wiz.visible_force_done)
        wiz.action_force_done()
        self.assertEqual(self._picked(move_a), 3)
        self.assertFalse(move_b.move_line_ids.filtered("qty_picked"))

    def test_untracked_product_reads_split_across_siblings(self):
        """Repeated untracked reads do not overfill a move with a pending
        sibling."""
        product = self.product_wo_tracking
        self.StockQuant.create(
            {
                "product_id": product.id,
                "location_id": self.stock_location.id,
                "quantity": 2,
            }
        )
        picking = self._create_multi_move_picking(product, [2, 1])
        picking.action_assign()
        move_a, move_b = self._get_sibling_moves(picking, product)
        self.assertEqual(len(move_a.move_line_ids), 1)
        self.assertFalse(move_b.move_line_ids)
        self.env["stock.quant"]._update_available_quantity(
            product, self.stock_location, 2
        )
        wiz = self._open_wizard(picking)
        for _index in range(3):
            self._scan_unit(wiz, product)
        self.assertEqual(self._picked(move_a), 2)
        self.assertEqual(self._picked(move_b), 1)
        self.assertNotIn("higher than necessary", wiz.message)

    def test_manual_qty_splits_across_siblings(self):
        """A manual entry covering several sibling moves splits by demand."""
        product = self.product_wo_tracking
        self.StockQuant.create(
            {
                "product_id": product.id,
                "location_id": self.stock_location.id,
                "quantity": 2,
            }
        )
        picking = self._create_multi_move_picking(product, [2, 1])
        picking.action_assign()
        move_a, move_b = self._get_sibling_moves(picking, product)
        self.env["stock.quant"]._update_available_quantity(
            product, self.stock_location, 2
        )
        wiz = self._open_wizard(picking)
        wiz.manual_entry = True
        wiz.product_id = product
        wiz.location_id = self.stock_location
        wiz.product_qty = 3
        wiz.action_confirm()
        self.assertEqual(self._picked(move_a), 2)
        self.assertEqual(self._picked(move_b), 1)
