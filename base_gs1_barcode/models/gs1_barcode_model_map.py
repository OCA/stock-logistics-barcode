# Copyright 2019 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class GS1BarcodeModelMap(models.Model):
    _name = 'gs1_barcode.model.map'

    @api.model
    def _get_tier_validation_model_names(self):
        res = []
        return res

    model_id = fields.Many2one(
        comodel_name="ir.model",
        string="Referenced Model",
        required=True,
    )
    model = fields.Char(
        related='model_id.model', index=True, store=True,
    )
    field_id = fields.Many2one(
        'ir.model.fields',
        required=True,
        domain="[('model_id', '=', model_id)]",
    )
    gs1_barcode_id = fields.Many2one(
        'gs1_barcode',
        required=True,
    )
    ai = fields.Char(
        related='gs1_barcode_id.ai',
    )

    _sql_constraints = [
        ('gs1_model_field_uniq', 'unique (model_id,field_id,gs1_barcode_id)',
         "There cannot be two repeated mappings of "
         "the GS1 code to model and field.")]

    @api.onchange('model_id')
    def onchange_model_id(self):
        return {'domain': {
            'model_id': [
                ('model', 'in', self._get_tier_validation_model_names())]}}
