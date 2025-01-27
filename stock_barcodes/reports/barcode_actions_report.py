from odoo import api, models


class ReportStockBarcodesBarcodeActions(models.Model):
    _name = "report.stock_barcodes.report_barcode_actions"
    _description = "Print barcodes from barcode actions"

    @api.model
    def _get_report_values(self, docids, data=None):
        datas = self.env["stock.barcodes.action"].search_read(
            [("id", "in", docids), ("barcode", "!=", False)],
            ["name", "barcode", "barcode_image"],
        )
        return {
            "barcodes": datas,
        }
