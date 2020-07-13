from odoo import models, _


class WizStockBarcodesRead(models.AbstractModel):
    _inherit = 'wiz.stock.barcodes.read'

    def process_barcode(self, barcode):
        domain = self._barcode_domain(barcode)
        product = self.env['product.product'].search(domain)
        if not product:
            # also search by multiple EAN
            product = self.env['product.product'].search([
                ('ean13_ids.name', '=', barcode)])
            if len(product) > 1:
                self._set_messagge_info(
                    'more_match', _('More than one product found'))
                return
            if product:
                self.action_product_scaned_post(product)
                self.action_done()
                self._set_messagge_info('success', _('Barcode read correctly'))
                return
        return super(WizStockBarcodesRead, self).process_barcode(barcode)
