import logging
import re

from odoo import tools, models, fields, api, _
from odoo.exceptions import ValidationError


class BarcodeRule(models.Model):
    _inherit = 'barcode.rule'

    model_ids = fields.Many2many(
        string="Applicable models",
        comodel_name="ir.model",
        domain=[('field_id.name', '=', '_barcode_scanned')])
