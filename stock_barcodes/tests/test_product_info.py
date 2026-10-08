# Copyright 2026 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from datetime import timedelta

from odoo import Command, fields
from odoo.tests import tagged

from .test_scan_uom import ScanUomCommon


@tagged("post_install", "-at_install")
class TestProductInfo(ScanUomCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product = cls.Product.create(
            {
                "name": "Product in several locations",
                "barcode": "LOCATION-STOCK",
                "is_storable": True,
            }
        )
        now = fields.Datetime.now()
        # location_2 holds the oldest stock, so FIFO takes it first
        cls.StockQuant._update_available_quantity(
            cls.product, cls.location_2, 5, in_date=now - timedelta(days=2)
        )
        cls.StockQuant._update_available_quantity(
            cls.product, cls.location_1, 3, in_date=now - timedelta(days=1)
        )
        # Stock out of the warehouse stock location is not listed
        cls.StockQuant._update_available_quantity(
            cls.product, cls.stock_location_internal, 7
        )

    def _create_picking(self, incoming, demand):
        picking_type = self.env.ref(
            "stock.picking_type_in" if incoming else "stock.picking_type_out"
        )
        if incoming:
            source = self.env.ref("stock.stock_location_suppliers")
            destination = self.stock_location
        else:
            source = self.stock_location
            destination = self.env.ref("stock.stock_location_customers")
        picking = self.StockPicking.create(
            {
                "picking_type_id": picking_type.id,
                "location_id": source.id,
                "location_dest_id": destination.id,
                "move_ids": [
                    Command.create(
                        {
                            "name": self.product.display_name,
                            "product_id": self.product.id,
                            "product_uom": self.product.uom_id.id,
                            "product_uom_qty": demand,
                            "location_id": source.id,
                            "location_dest_id": destination.id,
                        }
                    )
                ],
            }
        )
        picking.action_confirm()
        return picking

    def _open_location_stock(self, picking):
        action = picking.action_barcode_scan(option_group=self.scan_options)
        wizard = self.WizScanReadPicking.browse(action["res_id"])
        self.action_barcode_scanned(wizard, self.product.barcode)
        action = wizard.action_open_product_info()
        self.assertEqual(action["target"], "new")
        return wizard, self.env[action["res_model"]].browse(action["res_id"])

    def test_outgoing_lists_removal_order_and_sets_source(self):
        self._create_picking(incoming=True, demand=4)
        picking = self._create_picking(incoming=False, demand=2)
        wizard, location_stock = self._open_location_stock(picking)
        self.assertEqual(location_stock.product_id, self.product)
        self.assertEqual(location_stock.qty_available, 8)
        self.assertEqual(location_stock.incoming_qty, 4)
        self.assertEqual(location_stock.outgoing_qty, 2)
        self.assertEqual(location_stock.virtual_available, 10)
        self.assertEqual(
            location_stock.line_ids.location_id, self.location_2 + self.location_1
        )
        self.assertEqual(location_stock.line_ids.mapped("quantity"), [5, 3])
        location_dest = wizard.location_dest_id
        result = location_stock.line_ids[1].action_select()
        self.assertEqual(result["type"], "ir.actions.act_window_close")
        self.assertEqual(wizard.location_id, self.location_1)
        self.assertEqual(wizard.location_dest_id, location_dest)
        self.assertEqual(wizard.qty_available, 3)

    def test_incoming_lists_reverse_order_and_sets_destination(self):
        picking = self._create_picking(incoming=True, demand=4)
        wizard, location_stock = self._open_location_stock(picking)
        self.assertEqual(location_stock.qty_available, 8)
        self.assertEqual(location_stock.incoming_qty, 4)
        self.assertEqual(location_stock.outgoing_qty, 0)
        self.assertEqual(location_stock.virtual_available, 12)
        self.assertEqual(
            location_stock.line_ids.location_id, self.location_1 + self.location_2
        )
        location = wizard.location_id
        location_stock.line_ids[1].action_select()
        self.assertEqual(wizard.location_dest_id, self.location_2)
        self.assertEqual(wizard.location_id, location)

    def test_inventory_lists_warehouse_locations(self):
        wizard = self.WizScanReadInventory.create(
            {"option_group_id": self.scan_options.id, "step": 1}
        )
        wizard.product_id = self.product
        action = wizard.action_open_product_info()
        location_stock = self.env[action["res_model"]].browse(action["res_id"])
        self.assertEqual(
            location_stock.line_ids.location_id, self.location_2 + self.location_1
        )
        location_stock.line_ids[0].action_select()
        self.assertEqual(wizard.location_id, self.location_2)

    def test_select_location_only(self):
        picking = self._create_picking(incoming=False, demand=2)
        action = picking.action_barcode_scan(option_group=self.scan_options)
        wizard = self.WizScanReadPicking.browse(action["res_id"])
        self.action_barcode_scanned(wizard, self.product.barcode)
        action = wizard.action_select_location_stock()
        location_stock = self.env[action["res_model"]].browse(action["res_id"])
        self.assertFalse(location_stock.show_product_info)
        location_stock.line_ids[1].action_select()
        self.assertEqual(wizard.location_id, self.location_1)

    def test_internal_buttons_force_field_and_order(self):
        picking_type = self.env.ref("stock.picking_type_internal")
        picking = self.StockPicking.create(
            {
                "picking_type_id": picking_type.id,
                "location_id": self.stock_location.id,
                "location_dest_id": self.stock_location.id,
                "move_ids": [
                    Command.create(
                        {
                            "name": self.product.display_name,
                            "product_id": self.product.id,
                            "product_uom": self.product.uom_id.id,
                            "product_uom_qty": 2,
                            "location_id": self.stock_location.id,
                            "location_dest_id": self.stock_location.id,
                        }
                    )
                ],
            }
        )
        picking.action_confirm()
        action = picking.action_barcode_scan(option_group=self.scan_options)
        wizard = self.WizScanReadPicking.browse(action["res_id"])
        self.action_barcode_scanned(wizard, self.product.barcode)
        # Contexts set by the source and destination location buttons
        source_ctx = {"location_stock_field": "location_id"}
        dest_ctx = {
            "location_stock_field": "location_dest_id",
            "location_stock_reverse": True,
        }
        for context, field, locations in (
            ({}, "location_id", self.location_2 + self.location_1),
            (source_ctx, "location_id", self.location_2 + self.location_1),
            (dest_ctx, "location_dest_id", self.location_1 + self.location_2),
        ):
            action = wizard.with_context(**context).action_select_location_stock()
            location_stock = self.env[action["res_model"]].browse(action["res_id"])
            self.assertEqual(location_stock.location_field, field)
            self.assertEqual(location_stock.line_ids.location_id, locations)
            location_stock.line_ids[0].action_select()
            self.assertEqual(wizard[field], locations[0])
        # The product information keeps its own criteria
        action = wizard.action_open_product_info()
        location_stock = self.env[action["res_model"]].browse(action["res_id"])
        self.assertEqual(location_stock.location_field, "location_id")
        self.assertEqual(
            location_stock.line_ids.location_id, self.location_2 + self.location_1
        )
