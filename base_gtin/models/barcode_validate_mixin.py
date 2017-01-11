# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, api, models, _
from odoo.exceptions import ValidationError


class BarcodeValidateAbstract(models.AbstractModel):
    _name = 'barcode.validate.abstract'

    barcode_type = fields.Selection(
        selection=lambda s: s._select_barcode_types(),
        default=lambda s: s.env.user.company_id.default_barcode_type,
    )

    @api.model
    def _select_barcode_types(self):
        """ Return the barcode types that are defined.

        This is necessary so that the types remain in-sync with core.
        """
        field = self.env['ir.model.fields'].search([
            ('model', '=', 'barcode.rule'),
            ('name', '=', 'type'),
        ])
        return field._get_type_selection(self.env)

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
