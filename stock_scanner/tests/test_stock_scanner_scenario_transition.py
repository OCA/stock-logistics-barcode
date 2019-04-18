# Copyright 2017 SYLEAM Info Services
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import exceptions
from odoo.tests import common
from odoo.tools.misc import mute_logger


class TestStockScannerScenarioTransition(common.TransactionCase):
    def test_transition_scenarios(self):
        """ Should raise if steps of a transition are on different scenarios
        """
        transition = self.env.ref(
            'stock_scanner.'
            'scanner_scenario_transition_sentinel_intro_scroll')
        other_scenario_step = self.env.ref(
            'stock_scanner.'
            'scanner_scenario_step_step_types_introduction')
        with self.assertRaises(exceptions.ValidationError):
            transition.to_id = other_scenario_step

    def test_transition_condition_syntax(self):
        """ Should raise if the condition contains syntax errors """
        transition = self.env.ref(
            'stock_scanner.'
            'scanner_scenario_transition_sentinel_intro_scroll')
        with self.assertRaises(exceptions.ValidationError):
            with mute_logger('stock_scanner'):
                transition.condition = 'function('
