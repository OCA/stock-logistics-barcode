# -*- coding: utf-8 -*-
  
from odoo import models, api


class BarcodeEventsMixin(models.AbstractModel):
    _inherit = 'barcodes.barcode_events_mixin'

    @api.onchange('_barcode_scanned')
    def _on_barcode_scanned(self):
        self.env.cache['_barcode_active_model'] = self._name
        return super(BarcodeEventsMixin, self)._on_barcode_scanned()
