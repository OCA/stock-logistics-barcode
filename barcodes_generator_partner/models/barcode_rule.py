# Copyright (C) 2014-Today GRAP (http://www.grap.coop)
# Copyright (C) 2016-Today La Louve (http://www.lalouve.net)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields


class BarcodeRule(models.Model):
    _inherit = 'barcode.rule'

    generate_model = fields.Selection(
        selection_add=[('res.partner', 'Partners')])

    type = fields.Selection(
        selection_add=[
            ('client', 'Client'),
        ]
    )
