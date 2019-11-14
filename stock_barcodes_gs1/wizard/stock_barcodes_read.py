# Copyright 2019 Sergio Teruel <sergio.teruel@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import _, models


class WizStockBarcodesRead(models.AbstractModel):
    _inherit = 'wiz.stock.barcodes.read'

    def _prepare_lot_values(self, barcode_decoded):
        lot_barcode = barcode_decoded.get('10', False)
        return {
            'name': lot_barcode,
            'product_id': self.product_id.id,
        }

    def _create_lot(self, barcode_decoded):
        return self.env['stock.production.lot'].create(
            self._prepare_lot_values(barcode_decoded))

    def process_lot(self, barcode_decoded):
        lot_barcode = barcode_decoded.get('10', False)
        lot = self.env['stock.production.lot'].search([
            ('name', '=', lot_barcode),
            ('product_id', '=', self.product_id.id),
        ])
        if not lot:
            lot = self._create_lot(barcode_decoded)
        self.lot_id = lot

    def process_barcode(self, barcode):
        """ Only has been implemented AI (01, 02, 10, 37), so is possible that
        scanner reads a barcode ok but this one is not precessed.
        """
        model_map = self.env['gs1_barcode.model.map'].search([])
        try:
            barcode_decoded = self.env['gs1_barcode'].decode(barcode)
        except Exception:
            return super().process_barcode(barcode)
        processed = False
        model = self.env.ref(
            'stock_barcodes_gs1.model_wiz_stock_barcodes_read')
        package_field = self.env.ref(
            'stock_barcodes.field_wiz_stock_barcodes_read_packaging_id')
        package_map = model_map.filtered(
            lambda m: m.model_id == model
            and m.field_id == package_field)
        package_barcode = barcode_decoded.get(package_map.ai, False)
        product_field = self.env.ref(
            'stock_barcodes.field_wiz_stock_barcodes_read_product_id')
        product_map = model_map.filtered(
            lambda m: m.model_id == model
            and m.field_id == product_field)
        product_barcode = barcode_decoded.get(product_map.ai, False)
        lot_field = self.env.ref(
            'stock_barcodes.field_wiz_stock_barcodes_read_lot_id')
        lot_map = model_map.filtered(
            lambda m: m.model_id == model
            and m.field_id == lot_field)
        lot_barcode = barcode_decoded.get(lot_map.ai, False)
        product_qty_field = self.env.ref(
            'stock_barcodes.field_wiz_stock_barcodes_read_product_qty')
        lot_map = model_map.filtered(
            lambda m: m.model_id == model
            and m.field_id == product_qty_field)
        product_qty = barcode_decoded.get(lot_map.ai, False)
        if product_barcode:
            product = self.env['product.product'].search(
                self._barcode_domain(product_barcode))
            if not product:
                self._set_messagge_info(
                    'not_found', _('Barcode for product not found'))
                return False
            else:
                processed = True
                self.action_product_scaned_post(product)
        if package_barcode:
            packaging = self.env['product.packaging'].search(
                self._barcode_domain(package_barcode))
            if not packaging:
                self._set_messagge_info(
                    'not_found', _('Barcode for product packaging not found'))
                return False
            else:
                if len(packaging) > 1:
                    self._set_messagge_info(
                        'more_match', _('More than one package found'))
                    return False
                processed = True
                self.action_packaging_scaned_post(packaging)
        if lot_barcode and self.product_id.tracking != 'none':
            self.process_lot(barcode_decoded)
            processed = True
        if product_qty:
            self.product_qty = product_qty
        if processed:
            self.action_done()
            self._set_messagge_info('success', _('Barcode read correctly'))
            return True
        self._set_messagge_info('not_found', _('Barcode not found'))
        return False
