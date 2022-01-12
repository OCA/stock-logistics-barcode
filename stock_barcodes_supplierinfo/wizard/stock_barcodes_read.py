# Copyright 2022 NuoBiT - Kilian Niubo <kniubo@nuobit.com>
# Copyright 2022 NuoBiT - Eric Antones <eantones@nuobit.com>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
from odoo import _, models


class WizStockBarcodesRead(models.AbstractModel):
    _inherit = "wiz.stock.barcodes.read"

    def process_barcode(self, barcode):
        self._set_messagge_info("success", _("Barcode read correctly"))
        domain = self._barcode_domain(barcode)
        product = self.env["product.product"].search(domain)
        if not product:
            # search product by supplier barcode
            supplierinfo = self.env["product.supplierinfo"].search(
                [("barcode", "=", barcode)]
            )
            if supplierinfo:
                product = (
                    supplierinfo.product_id
                    or supplierinfo.product_tmpl_id.product_variant_ids
                )
                if len(product) > 1:
                    self._set_messagge_info(
                        "more_match", _("More than one product found")
                    )
                    return
                if product:
                    self.action_product_scaned_post(product)
                    self.action_done()
                    return
        return super(WizStockBarcodesRead, self).process_barcode(barcode)
