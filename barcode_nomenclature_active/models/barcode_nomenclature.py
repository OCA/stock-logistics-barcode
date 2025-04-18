# Copyright (C) 2025-Today: Sylvain LE GAL, GRAP (http://www.grap.coop)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class BarcodeNomenclature(models.Model):
    _inherit = "barcode.nomenclature"

    active = fields.Boolean(default=True)
