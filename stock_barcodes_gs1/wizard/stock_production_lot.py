# Copyright 2019 Sergio Teruel <sergio.teruel@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import models


class WizStockBarcodesNewLot(models.TransientModel):
    _inherit = "wiz.stock.barcodes.new.lot"
    _description = "Wizard to create new lot from barcode scanner"

    def _decode_barcode(self, barcode):
        return self.env["gs1_barcode"].decode(barcode)

    def on_barcode_scanned(self, barcode):
        try:
            barcode_decoded = self._decode_barcode(barcode)
        except Exception:
            return super().on_barcode_scanned(barcode)
        package_barcode = barcode_decoded.get("01", False)
        product_barcode = barcode_decoded.get("02", False)
        if not product_barcode:
            # Sometimes the product does not yet have a GTIN. In this case
            # try the AI 240 'Additional product identification assigned
            # by the manufacturer'.
            product_barcode = barcode_decoded.get("240", False)
        lot_barcode = barcode_decoded.get("10", False)
        if not lot_barcode:
            return
        if package_barcode:
            packaging = self.env["product.packaging"].search(
                [("barcode", "=", package_barcode)]
            )
            if packaging:
                self.product_id = packaging.product_id
        elif product_barcode:
            product = self.env["product.product"].search(
                [("barcode", "=", product_barcode)]
            )
            if product:
                self.product_id = product
        self.lot_name = lot_barcode
