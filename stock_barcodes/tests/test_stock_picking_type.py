# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from unittest.mock import patch

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
