# -*- coding: utf-8 -*-
import logging

from odoo import _, api, exceptions, fields, models

_logger = logging.getLogger(__name__)

try:
    import barcode
except ImportError:
    _logger.debug("Cannot import 'viivakoodi' python library.")
    barcode = None


class BarcodeGenerateMixin(models.AbstractModel):
    _inherit = 'barcode.generate.mixin'

    lot_barcode_base = fields.Char(string='Barcode Base', copy=False)

    # View Section
    @api.multi
    def generate_base(self):
        for item in self:
            if item.barcode_rule_id.encoding != 'custom':
                super(BarcodeGenerateMixin, self).generate_base()
            else:
                if item.generate_type != 'sequence':
                    raise exceptions.UserError(_(
                        "Generate Base can be used only with barcode rule with"
                        " 'Generate Type' set to 'Base managed by Sequence'"))
                else:
                    item.lot_barcode_base = \
                        item.barcode_rule_id.sequence_id.next_by_id()

    @api.multi
    def generate_barcode(self):
        for item in self:
            if item.barcode_rule_id.encoding != 'custom':
                super(BarcodeGenerateMixin, self).generate_barcode()
            else:
                padding = item.barcode_rule_id.padding
                str_base = str(item.lot_barcode_base).rjust(padding, '0')
                custom_code = self._get_custom_barcode(item)
                item.barcode = custom_code.replace('.' * padding, str_base)
