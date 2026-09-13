# Copyright 2026 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import Command
from odoo.tests import Form, tagged

from .common import TestCommonStockBarcodes


class ScanUomCommon(TestCommonStockBarcodes):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.unit = cls.env.ref("uom.product_uom_unit")
        cls.dozen = cls.env.ref("uom.product_uom_dozen")
        cls.scan_options = cls.StockBarcodesOptionGroup.create(
            {
                "name": "Unit conversion scan",
                "source_pending_moves": "move_ids",
                "show_pending_moves": "all",
                "confirmed_moves": True,
                "allow_not_demanded_product": True,
                "option_ids": [
                    Command.create(
                        {
                            "name": field,
                            "field_name": field,
                            "step": 1,
                            "sequence": index,
                            "to_scan": field in ("product_id", "lot_id"),
                            "required": field != "lot_id",
                            "filled_default": field
                            in ("location_id", "location_dest_id"),
                        }
                    )
                    for index, field in enumerate(
                        ("product_id", "lot_id", "location_id", "location_dest_id")
                    )
                ],
            }
        )

    def _scan_picking(self, product, demand, uom, incoming=True):
        picking_type = self.env.ref(
            "stock.picking_type_in" if incoming else "stock.picking_type_out"
        )
        source = (
            self.env.ref("stock.stock_location_suppliers")
            if incoming
            else self.location_1
        )
        destination = (
            self.location_1
            if incoming
            else self.env.ref("stock.stock_location_customers")
        )
        picking = self.StockPicking.create(
            {
                "picking_type_id": picking_type.id,
                "location_id": source.id,
                "location_dest_id": destination.id,
                "move_ids": [
                    Command.create(
                        {
                            "name": product.display_name,
                            "product_id": product.id,
                            "product_uom": uom.id,
                            "product_uom_qty": demand,
                            "location_id": source.id,
                            "location_dest_id": destination.id,
                        }
                    )
                ],
            }
        )
        picking.action_confirm()
        picking.action_assign()
        action = picking.action_barcode_scan(option_group=self.scan_options)
        return picking, self.WizScanReadPicking.browse(action["res_id"])


@tagged("post_install", "-at_install")
class TestScanUom(ScanUomCommon):
    def test_packaging_changes_product_unit(self):
        product = self.Product.create(
            {
                "name": "Product sold by dozen",
                "barcode": "PRODUCT-DOZEN",
                "is_storable": True,
                "uom_id": self.dozen.id,
                "uom_po_id": self.dozen.id,
            }
        )
        packaging = self.ProductPackaging.create(
            {
                "name": "Two dozen",
                "product_id": product.id,
                "qty": 2,
                "barcode": "PACKAGING-TWO-DOZEN",
            }
        )
        self.scan_options.option_ids = [
            Command.create(
                {
                    "name": "Packaging",
                    "field_name": "packaging_id",
                    "step": 1,
                    "sequence": 10,
                    "to_scan": True,
                }
            )
        ]
        picking, wizard = self._scan_picking(product, 2, self.dozen)
        wizard.manual_entry = True
        self.action_barcode_scanned(wizard, self.product_wo_tracking.barcode)
        self.assertEqual(wizard.product_uom_id, self.unit)
        self.action_barcode_scanned(wizard, packaging.barcode)
        self.assertEqual(wizard.product_id, product)
        self.assertEqual(wizard.product_uom_id, self.dozen)
        wizard.product_qty = 2
        wizard.action_confirm()
        wizard.action_validate_picking()
        self.assertEqual(picking.state, "done")
        self.assertEqual(sum(picking.move_line_ids.mapped("quantity_product_uom")), 2)
        self.assertEqual(
            self.StockQuant._get_available_quantity(product, self.location_1), 2
        )

    def test_receive_one_unit_of_dozen_demand(self):
        picking, wizard = self._scan_picking(self.product_wo_tracking, 1, self.dozen)
        self.action_barcode_scanned(wizard, self.product_wo_tracking.barcode)
        self.assertEqual(picking.move_ids.qty_picked, 0.08)
        self.assertEqual(wizard.todo_line_ids.product_uom_qty, 12)
        self.assertEqual(wizard.todo_line_ids.qty_done, 1)
        self.assertEqual(wizard.todo_line_ids.qty_done_rest, 11)
        self.assertEqual(wizard.todo_line_ids.state, "pending")
        action = wizard.action_validate_picking()
        self.assertEqual(action["res_model"], "stock.backorder.confirmation")
        backorder = Form(
            self.env[action["res_model"]].with_context(**action["context"])
        ).save()
        backorder.process_cancel_backorder()
        self.assertEqual(picking.state, "done")
        self.assertEqual(sum(picking.move_line_ids.mapped("quantity_product_uom")), 1)

    def test_scan_reserved_dozen_line(self):
        self.StockQuant._update_available_quantity(
            self.product_wo_tracking, self.location_1, 12
        )
        picking, wizard = self._scan_picking(
            self.product_wo_tracking, 1, self.dozen, incoming=False
        )
        picking.move_line_ids.write({"product_uom_id": self.dozen.id, "quantity": 1})
        self.action_barcode_scanned(wizard, self.product_wo_tracking.barcode)
        self.assertEqual(picking.move_line_ids.product_uom_id, self.unit)
        self.assertEqual(picking.move_line_ids.qty_picked, 1)
        self.assertEqual(picking.move_ids.qty_picked, 0.08)
        self.assertEqual(picking.move_line_ids.barcode_scan_state, "pending")
        self.assertEqual(wizard.todo_line_ids.qty_done, 1)
        for _index in range(11):
            self.action_barcode_scanned(wizard, self.product_wo_tracking.barcode)
        self.assertEqual(picking.move_line_ids.qty_picked, 12)
        self.assertEqual(wizard.todo_line_ids.qty_done, 12)
        wizard.action_validate_picking()
        self.assertEqual(picking.state, "done")
        self.assertEqual(sum(picking.move_line_ids.mapped("quantity_product_uom")), 12)

    def test_manual_dozen_quantity_on_unit_lines(self):
        picking, wizard = self._scan_picking(self.product_wo_tracking, 12, self.unit)
        wizard.manual_entry = True
        self.action_barcode_scanned(wizard, self.product_wo_tracking.barcode)
        wizard.product_uom_id = self.dozen
        wizard.product_qty = 1
        wizard.action_confirm()
        self.assertEqual(picking.move_ids.qty_picked, 12)
        self.assertEqual(wizard.todo_line_ids.qty_done, 12)
        wizard.action_validate_picking()
        self.assertEqual(picking.state, "done")
        self.assertEqual(sum(picking.move_line_ids.mapped("quantity_product_uom")), 12)
