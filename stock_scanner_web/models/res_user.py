# Copyright 2016 Angel Moya <http://angelmoya.es>
# Copyright 2016 Eficent Business and IT Consulting Services, S.L.
# <http://www.eficent.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields


class ResUser(models.Model):
    _inherit = 'res.users'

    scanner_hardware_ids = fields.Many2many(
        comodel_name='scanner.hardware',
        relation='scanner_hardware_users_rel',
        column1='user_id',
        column2='hardware_id',
        string='Permitted Scanners')
