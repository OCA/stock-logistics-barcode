# -*- coding: utf-8 -*-
# Copyright 2021 Sunflower IT <https://sunflowerweb.nl>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class BarcodesMultilineDemoWizard(models.TransientModel):
    _name = 'barcodes_multiline.demo_wizard'
    _inherit = 'barcodes.barcode_events_mixin'

    text = fields.Text()

    def on_barcode_scanned(self, barcode):
        self.text = barcode
