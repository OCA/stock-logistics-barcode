# Copyright 2021 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import _, models


class WizStockBarcodesRead(models.AbstractModel):
    _inherit = "wiz.stock.barcodes.read"

    def barcode_quant_domain(self, barcode):
        domain = self._barcode_domain(barcode)
        domain.append(("location_id.usage", "=", "internal"))
        return domain

    def process_barcode(self, barcode):
        self._set_messagge_info("success", _("Barcode read correctly"))
        domain = self.barcode_quant_domain(barcode)
        quants = self.env["stock.quant"].search(domain)
        if len(quants) == 1:
            # All ok
            self.action_product_scaned_post(quants.product_id)
            if quants.lot_id:
                self.action_lot_scaned_post(quants.lot_id)
            if self.env.context.get("default_picking_type_code", False) == "outgoing":
                self.location_id = quants.location_id
            self.product_qty = quants.quantity
            if not self.manual_entry:
                self.action_done()
            return True
        elif len(quants) > 1:
            # More than one record found with same barcode.
            # Could be half lot in two distinct locations.
            # Empty location field to force a location barcode scan
            products = quants.mapped("product_id")
            if len(products) == 1:
                self.action_product_scaned_post(products[0])
            lots = quants.mapped("lot_id")
            if len(products) == 1:
                self.action_lot_scaned_post(lots[0])
            self._set_messagge_info("more_match", _("More than one location found"))
            self.location_id = False
            return False
        else:
            # No record found
            return super().process_barcode(barcode)
