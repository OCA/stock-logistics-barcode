# -*- coding: utf-8 -*-
# © 2011 Sylvain Garancher <sylvain.garancher@syleam.fr>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from psycopg2 import errorcodes

from openerp import models, api
from openerp import _


logger = logging.getLogger('stock_scanner')

_CURSES_COLORS = [
    ('black', _('Black')),
    ('blue', _('Blue')),
    ('cyan', _('Cyan')),
    ('green', _('Green')),
    ('magenta', _('Magenta')),
    ('red', _('Red')),
    ('white', _('White')),
    ('yellow', _('Yellow')),
]

PG_CONCURRENCY_ERRORS_TO_RETRY = (
    errorcodes.LOCK_NOT_AVAILABLE,
    errorcodes.SERIALIZATION_FAILURE,
    errorcodes.DEADLOCK_DETECTED)
MAX_TRIES_ON_CONCURRENCY_FAILURE = 5


class ScannerHardware(models.Model):
    _inherit = 'scanner.hardware'

    @api.model
    def _scenario_list(self, parent_id=False):
        """
        Remove log-in / log-out scenarios if we run under the web interface
        """

        if self.env.context.get('stock_scanner_call_from_web', False):
            scanner_scenario_obj = self.env['scanner.scenario']
            scanner_scenario_login = self.env.ref(
                'stock_scanner.scanner_scenario_login')
            scanner_scenario_logout = self.env.ref(
                'stock_scanner.scanner_scenario_logout')
            scanner_scenarios = scanner_scenario_obj.search(
                ['|',
                 ('warehouse_ids', '=', False),
                 ('warehouse_ids', 'in', [self.warehouse_id.id]),
                 ('parent_id', '=', parent_id)])
            scenario_names = [scenario.name for scenario in
                              scanner_scenarios if scenario not in (
                                  scanner_scenario_login,
                                  scanner_scenario_logout)]
            return scenario_names
        else:
            return super(ScannerHardware, self)._scenario_list(
                parent_id=parent_id)
