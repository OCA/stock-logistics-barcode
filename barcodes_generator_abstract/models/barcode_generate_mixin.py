# Copyright (C) 2014-TODAY GRAP (http://www.grap.coop)
# Copyright (C) 2016-TODAY La Louve (http://www.lalouve.net)
# Copyright 2017 LasLabs Inc.
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from odoo import _, api, exceptions, fields, models

from .barcode_rule import _GENERATE_TYPE

_logger = logging.getLogger(__name__)

try:
    import barcode
except ImportError:
    _logger.debug("Cannot import 'python-barcode' python library.")
    barcode = None


class BarcodeGenerateMixin(models.AbstractModel):
    _name = 'barcode.generate.mixin'
    _description = 'Generate Barcode Mixin'

    # Column Section
    barcode_rule_id = fields.Many2one(
        string='Barcode Rule', comodel_name='barcode.rule')

    barcode_base = fields.Integer(string='Barcode Base', copy=False)

    generate_type = fields.Selection(
        string='Generate Type', selection=_GENERATE_TYPE, readonly=True,
        related='barcode_rule_id.generate_type')

    @api.model
    def create(self, vals):
        """It creates a new barcode if automation is active."""
        barcode_rule = self.env['barcode.rule'].get_automatic_rule(self._name)
        if barcode_rule.exists():
            vals.update({
                'barcode_rule_id': barcode_rule.id,
            })
        record = super(BarcodeGenerateMixin, self).create(vals)
        if barcode_rule:
            record.generate_base()
            record.generate_barcode()
        return record

    # View Section
    @api.multi
    def generate_base(self):
        for item in self:
            if item.generate_type != 'sequence':
                raise exceptions.UserError(_(
                    "Generate Base can be used only with barcode rule with"
                    " 'Generate Type' set to 'Base managed by Sequence'"))
            else:
                item.barcode_base =\
                    item.barcode_rule_id.sequence_id.next_by_id()

    @api.multi
    def generate_barcode(self):
        for item in self:
            padding = item.barcode_rule_id.padding
            str_base = str(item.barcode_base).rjust(padding, '0')
            custom_code = self._get_custom_barcode(item)
            if custom_code:
                custom_code = custom_code.replace('.' * padding, str_base)
                barcode_class = barcode.get_barcode_class(
                    item.barcode_rule_id.encoding)
                item.barcode = barcode_class(custom_code)

    # Custom Section
    @api.model
    def _get_custom_barcode(self, item):
        """
        If the pattern is '23.....{NNNDD}'
        this function will return '23.....00000'
        Note : Overload _get_replacement_char to have another char
        instead that replace 'N' and 'D' char.
        """
        if not item.barcode_rule_id:
            return False

        # Define barcode
        custom_code = item.barcode_rule_id.pattern
        custom_code = custom_code.replace('{', '').replace('}', '')
        custom_code = custom_code.replace(
            'D', self._get_replacement_char('D'))
        return custom_code.replace(
            'N', self._get_replacement_char('N'))

    @api.model
    def _get_replacement_char(self, char):
        """
        Can be overload by inheritance
        Define wich character will be used instead of the 'N' or the 'D'
        char, present in the pattern of the barcode_rule_id
        """
        return '0'
