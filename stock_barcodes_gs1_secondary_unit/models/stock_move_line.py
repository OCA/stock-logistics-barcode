# Copyright 2019 Sergio Teruel <sergio.teruel@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import models


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    def _barcodes_process_line_to_unlink(self):
        res = super()._barcodes_process_line_to_unlink()
        self.secondary_uom_qty = 0.0
        return res
