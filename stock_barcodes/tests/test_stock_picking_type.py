# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from unittest.mock import patch

from odoo import Command
from odoo.tests.common import tagged

from .common import TestCommonStockBarcodes


@tagged("post_install", "-at_install")
class TestStockPickingType(TestCommonStockBarcodes):
    def test_action_barcode_new_picking(self):
        with patch.object(
            type(self.StockPicking), "action_barcode_scan"
        ) as mock_picking_type:
            result = self.stock_picking_type.action_barcode_new_picking()
            self.assertTrue(bool(result))
            mock_picking_type.assert_called_once()

    def test_action_barcode_scan_outgoing(self):
        picking_type = self.env.ref("stock.picking_type_out")
        picking_type.barcode_option_group_id = self.option_group
        action = picking_type.action_barcode_scan()
        self.assertEqual(action["res_model"], "wiz.stock.barcodes.read.picking")
        wiz = self.WizScanReadPicking.browse(action["res_id"])
        self.assertEqual(wiz.res_id, picking_type.id)
        self.assertEqual(wiz.picking_type_code, "outgoing")
        self.assertEqual(wiz.option_group_id, self.option_group)
        self.assertEqual(
            wiz.location_dest_id,
            picking_type.default_location_dest_id
            or self.env.ref("stock.stock_location_customers"),
        )

    def test_action_barcode_scan_incoming(self):
        picking_type = self.env.ref("stock.picking_type_in")
        picking_type.barcode_option_group_id = self.option_group
        wiz = self.WizScanReadPicking.browse(
            picking_type.action_barcode_scan()["res_id"]
        )
        self.assertEqual(wiz.picking_type_code, "incoming")
        self.assertEqual(
            wiz.location_id,
            picking_type.default_location_src_id
            or self.env.ref("stock.stock_location_suppliers"),
        )

    def test_action_barcode_scan_filled_default_locations(self):
        option_group = self.StockBarcodesOptionGroup.create(
            {
                "name": "Filled default locations",
                "option_ids": [
                    Command.create(
                        {
                            "step": 1,
                            "name": "Location",
                            "field_name": "location_id",
                            "filled_default": True,
                        }
                    ),
                    Command.create(
                        {
                            "step": 2,
                            "name": "Location dest",
                            "field_name": "location_dest_id",
                            "filled_default": True,
                        }
                    ),
                ],
            }
        )
        picking_type = self.env.ref("stock.picking_type_internal")
        picking_type.write(
            {
                "barcode_option_group_id": option_group.id,
                "default_location_src_id": self.location_1.id,
                "default_location_dest_id": self.location_2.id,
            }
        )
        wiz = self.WizScanReadPicking.browse(
            picking_type.action_barcode_scan()["res_id"]
        )
        self.assertEqual(wiz.location_id, self.location_1)
        self.assertEqual(wiz.location_dest_id, self.location_2)
