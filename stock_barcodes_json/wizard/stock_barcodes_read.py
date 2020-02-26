# Copyright 2019 Sergio Teruel <sergio.teruel@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import _, fields, models
from odoo.tools.safe_eval import safe_eval


class WizStockBarcodesRead(models.AbstractModel):
    _inherit = 'wiz.stock.barcodes.read'

    def compute_mapping(self):
        model = self.browse([])
        # todo: proper domain using model maybe
        self.mapping_id = self.env['wiz.stock.barcodes.mapping'].search([], limit=1)

    mapping_id = fields.Many2one('wiz.stock.barcodes.mapping', compute=compute_mapping)

    def process_barcode(self, barcode):

        try:
            barcode_decoded = safe_eval(barcode)
            vals = {}
            for key,val in barcode_decoded.items():
                mapping = self.mapping_id.item_ids.filtered(lambda m: m.key == key)
                if mapping:
                    vals[mapping.value] = val

        except Exception:
            return super().process_barcode(barcode)

        barcode_decoded = safe_eval(self.barcode)

        if 'product_id' in vals.keys():
            # Check if product exists
            self.product_id = vals['product_id']
            processed = True
        if 'product_barcode' in vals.keys():
            # Check if product exists, based on the product barcode
            product = self.env['product.product'].search(
                self._barcode_domain(vals['product_barcode']))
            if not product:
                self._set_messagge_info(
                    'not_found', _('Barcode for product not found'))
                return False
            else:
                processed = True
                self.action_product_scaned_post(product)
        if 'package_barcode' in vals.keys():
            # Search package
            packaging = self.env['product.packaging'].search(
                self._barcode_domain(vals['package_barcode']))
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
        if 'lot_barcode' in vals.keys():
            # Search lot based on barcode
            self.process_lot(vals['lot_barcode'])
        if 'product_qty' in vals.keys():
            self.product_qty = vals['product_qty']

        processed = True
        if processed:
            self.action_done()
            self._set_messagge_info('success', _('Barcode read correctly'))
            return True
        self._set_messagge_info('not_found', _('Barcode not found'))
        return False

class WizStockBarcodesMappingItem(models.Model):
    _name = 'wiz.stock.barcodes.mapping.item'
    _description = 'Barcode Item'
    _rec_name = 'key'

    mapping_id = fields.Many2one('wiz.stock.barcodes.mapping')
    key = fields.Char() # to do: selection to ir_fields
    value = fields.Char()

class WizStockBarcodesMapping(models.Model):
    _name = 'wiz.stock.barcodes.mapping'
    _description = 'Barcode Mapping'
    _rec_name = 'model_id'

    model_id = fields.Many2one('ir.model')
    item_ids = fields.One2many('wiz.stock.barcodes.mapping.item', 'mapping_id')
