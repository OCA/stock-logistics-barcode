# Copyright 2019 Sergio Teruel <sergio.teruel@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import _, models


class WizStockBarcodesRead(models.AbstractModel):
    _inherit = "wiz.stock.barcodes.read"

    def _prepare_lot_values(self, barcode_decoded):
        lot_barcode = barcode_decoded.get("10", False)
        return {
            "name": lot_barcode,
            "product_id": self.product_id.id,
            "company_id": self.env.company.id,
        }

    def _create_lot(self, barcode_decoded):
        return self.env["stock.production.lot"].create(
            self._prepare_lot_values(barcode_decoded)
        )

    def process_lot(self, barcode_decoded):
        lot_barcode = barcode_decoded.get("10", False)
        lot = self.env["stock.production.lot"].search(
            [("name", "=", lot_barcode), ("product_id", "=", self.product_id.id)]
        )
        if not lot and self.option_group_id.create_lot:
            lot = self._create_lot(barcode_decoded)
        self.lot_id = lot

    def _process_product_qty_gs1(self, product_qty):
        """Extend for custom processing of product qty."""
        return product_qty

    def process_barcode_package(self, package_barcode, processed):
        packaging = self.env["product.packaging"].search(
            self._barcode_domain(package_barcode)
        )
        if not packaging:
            self._set_messagge_info(
                "not_found", _("Barcode for product packaging not found")
            )
            return False
        else:
            if len(packaging) > 1:
                self._set_messagge_info("more_match", _("More than one package found"))
                return False
            self.action_packaging_scaned_post(packaging)

    def process_barcode(self, barcode):
        """ Only has been implemented AI (01, 02, 10, 37), so is possible that
        scanner reads a barcode ok but this one is not precessed.
        """
        try:
            barcode_decoded = self.env["gs1_barcode"].decode(barcode)
        except Exception:
            return super().process_barcode(barcode)
        processed = False
        package_barcode = barcode_decoded.get("01", False)
        product_barcode = barcode_decoded.get("02", False)
        if not product_barcode:
            # Sometimes the product does not yet have a GTIN. In this case
            # try the AI 240 'Additional product identification assigned
            # by the manufacturer'.
            product_barcode = barcode_decoded.get("240", False)
        lot_barcode = barcode_decoded.get("10", False)
        product_qty = barcode_decoded.get("37", False)
        if product_barcode:
            product = self.env["product.product"].search(
                self._barcode_domain(product_barcode)
            )
            if not product and not package_barcode:
                # If we did not found a product and we have not a package, maybe we
                # can try to use this product barcode as a packaging barcode
                package_barcode = product_barcode
            elif not product:
                self._set_messagge_info("not_found", _("Barcode for product not found"))
                return False
            else:
                processed = True
                self.action_product_scaned_post(product)
        if package_barcode:
            value_returned = self.process_barcode_package(package_barcode, processed)
            if value_returned is not None:
                return value_returned
        if lot_barcode and self.product_id.tracking != "none":
            self.process_lot(barcode_decoded)
            processed = True
        if product_qty and package_barcode:
            # If we have processed a package, we need to multiply it
            product_qty = self._process_product_qty_gs1(product_qty)
            self.product_qty = self.product_qty * product_qty
        elif product_qty:
            product_qty = self._process_product_qty_gs1(product_qty)
            self.product_qty = product_qty
        if not self.product_qty:
            # This could happen with double GS1-128 barcodes
            if self.packaging_id:
                self.packaging_qty = 0.0 if self.manual_entry else 1.0
                self.product_qty = self.packaging_id.qty * self.packaging_qty
            else:
                self.product_qty = 0.0 if self.manual_entry else 1.0
        if processed:
            if not self.check_option_required():
                return False
            self.action_confirm()
            self._set_messagge_info("success", _("Barcode read correctly"))
            return True
        return super().process_barcode(barcode)
