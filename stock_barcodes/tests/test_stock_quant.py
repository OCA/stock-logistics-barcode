# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from unittest.mock import patch

from odoo.tests.common import tagged

from .common import TestCommonStockBarcodes


@tagged("post_install", "-at_install")
class TestStockQuant(TestCommonStockBarcodes):
    def test_operation(self):
        with patch.object(
            type(self.quant_lot_1), "enable_current_operations"
        ) as mock_operation:
            self.quant_lot_1.inventory_quantity = 10
            self.quant_lot_1.operation_quantities_rest()
            self.assertEqual(self.quant_lot_1.inventory_quantity, 9)

            self.quant_lot_1.operation_quantities()
            self.assertEqual(self.quant_lot_1.inventory_quantity, 10)

            self.assertEqual(mock_operation.call_count, 2)

        with patch.object(type(self.quant_lot_1), "send_bus_done"), patch.object(
            type(self.quant_lot_1), "action_apply_inventory"
        ) as mock_operation:
            self.quant_lot_1.action_apply_inventory()
            self.assertTrue(mock_operation.called)
