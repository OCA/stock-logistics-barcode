# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from unittest.mock import patch

from odoo.tests.common import tagged

from .common import TestCommonStockBarcodes


@tagged("post_install", "-at_install")
class TestbarcodeActionsReport(TestCommonStockBarcodes):
    def test_get_report_values(self):
        barcode_action = self.StockBarcodeAction.create(
            {
                "name": "Barcode action valid",
                "action_window_id": self.env.ref("stock.stock_picking_type_action").id,
                "context": "{'search_default_barcode_options': 1}",
                "barcode": "1597536243",
            }
        )
        with patch.object(type(self.StockBarcodeAction), "search_read"), patch.object(
            type(self.env["report.stock_barcodes.report_barcode_actions"]),
            "_get_report_values",
            return_value={"barcodes": barcode_action},
        ) as mock_msg:
            result = self.env[
                "report.stock_barcodes.report_barcode_actions"
            ]._get_report_values(
                docids=[
                    barcode_action.id,
                ]
            )
            self.assertEqual(len(result["barcodes"]), 1)

            mock_msg.assert_called_once()
