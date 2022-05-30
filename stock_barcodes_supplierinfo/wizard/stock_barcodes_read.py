from odoo import models, _


class WizStockBarcodesRead(models.AbstractModel):
    _inherit = 'wiz.stock.barcodes.read'

    def process_barcode(self, barcode):
        domain = self._barcode_domain(barcode)
        product = self.env['product.product'].search(domain)
        if not product:
            # also search by supplier barcode
            product = self.env['product.product'].search([
                ('seller_ids.barcode', '=', barcode)])
            if product:
                if len(product) > 1:
                    self._set_messagge_info(
                        'more_match', _('More than one product found'))
                    return
                self.action_product_scaned_post(product)
                self.action_done()
                return
        return super(WizStockBarcodesRead, self).process_barcode(barcode)
