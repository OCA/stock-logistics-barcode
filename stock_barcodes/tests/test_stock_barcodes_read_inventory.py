# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from unittest.mock import patch

from odoo.tests.common import tagged

from .common import TestCommonStockBarcodes


@tagged("post_install", "-at_install")
class TestStockBarcodesReadInventory(TestCommonStockBarcodes):
    def test_action_display_read_quant(self):
        self.wiz_scan_read_inventory.action_display_read_quant()
        self.assertFalse(self.wiz_scan_read_inventory.display_read_quant)

        self.wiz_scan_read_inventory.display_read_quant = False
        self.wiz_scan_read_inventory.action_display_read_quant()
        self.assertTrue(self.wiz_scan_read_inventory.display_read_quant)

    def test_add_inventory_quant_done(self):
        self.wiz_scan_read_inventory.product_id = self.product_tracking.id
        self.wiz_scan_read_inventory.location_id = self.location_1.id
        self.wiz_scan_read_inventory.product_qty = 10
        self.wiz_scan_read_inventory.lot_id = self.lot_1.id
        self.wiz_scan_read_inventory.package_id = self.quant_package_1.id
        result = self.wiz_scan_read_inventory._add_inventory_quant()
        self.assertTrue(result)

        with patch.object(
            type(self.wiz_scan_read_inventory), "_add_inventory_quant"
        ), patch.object(
            type(self.wiz_scan_read_inventory), "action_clean_values"
        ) as mock_msg:
            self.wiz_scan_read_inventory.action_done()
            mock_msg.assert_called_once()

        with patch.object(
            type(self.wiz_scan_read_inventory), "_serial_tracking_message_fail"
        ) as mock_msg:
            self.wiz_scan_read_inventory.product_id = self.product_tracking_serial.id
            result = self.wiz_scan_read_inventory._add_inventory_quant()
            self.assertFalse(result)
            mock_msg.assert_called_once()

    def test_action_clean_values(self):
        with patch.object(
            type(self.wiz_scan_read_inventory), "send_bus_done"
        ) as mock_msg:
            self.wiz_scan_read_inventory.action_clean_values()
            self.assertEqual(self.wiz_scan_read_inventory.inventory_product_qty, 0)
            self.assertFalse(self.wiz_scan_read_inventory.package_id)
            self.assertFalse(self.wiz_scan_read_inventory.manual_entry)
            mock_msg.assert_called_once_with(
                "stock_barcodes_scan",
                "stock_barcodes_edit_manual",
                {
                    "manual_entry": False,
                },
            )

    def test_onchange_product_lot_id(self):
        self.wiz_scan_read_inventory.product_id = self.product_tracking.id
        self.wiz_scan_read_inventory.onchange_product_id()
        self.assertFalse(self.wiz_scan_read_inventory.lot_id)

        self.wiz_scan_read_inventory.lot_id = self.lot_1.id
        self.wiz_scan_read_inventory._onchange_lot_id()
        self.assertFalse(self.wiz_scan_read_inventory.auto_lot)
