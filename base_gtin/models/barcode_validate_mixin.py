# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, api, models, _
from odoo.exceptions import ValidationError


class BarcodeValidateAbstract(models.AbstractModel):
    _name = 'barcode.validate.abstract'

    barcode_type = fields.Selection(
        selection=lambda s: s.env['barcode.rule']._get_type_selection(),
        default=lambda s: s.env.user.company_id.default_barcode_type,
    )

    @api.multi
    def _barcode_validate(self, barcode_col):
        for rec_id in self:
            barcode = getattr(rec_id, barcode_col)
            barcode_type = rec_id.barcode_type
            res = self.env['barcode.nomenclature'].check_encoding(
                barcode, barcode_type,
            )
            if not res:
                raise ValidationError(
                    _('"%s" did not validate as a "%s" barcode type') % (
                        barcode, barcode_type,
                    )
                )
