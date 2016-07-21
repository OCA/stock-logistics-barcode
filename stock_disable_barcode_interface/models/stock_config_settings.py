# -*- coding: utf-8 -*-
# © 2016 ONESTEiN BV (<http://www.onestein.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields


class StockConfigSettings(models.TransientModel):
    _inherit = 'stock.config.settings'

    group_barcode_interface = fields.Boolean(
        'Enable barcode interface',
        implied_group='stock_disable_barcode_interface.group_enable_barcode')
