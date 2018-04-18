# Copyright 2017 SYLEAM Info Services
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from psycopg2 import IntegrityError

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

    def test_transition_name_scenario_unique(self):
        """Transition names should be unique within the same scenario."""
        step_from = self.env.ref(
            'stock_scanner.scanner_scenario_login_step_login')
        step_to = self.env.ref(
            'stock_scanner.scanner_scenario_login_step_done')

        # Create a new transition
        self.env['scanner.scenario.transition'].create({
            'from_id': step_from.id,
            'to_id': step_to.id,
            'name': 'Collision course!',
        })
        # we should still be able to create transitions w/ different names
        self.env['scanner.scenario.transition'].create({
            'from_id': step_from.id,
            'to_id': step_to.id,
            'name': 'This name is okay.',
        })
        # now, test that the constraint is intact
        with self.assertRaises(IntegrityError):
            self.env['scanner.scenario.transition'].create({
                'from_id': step_from.id,
                'to_id': step_to.id,
                'name': 'Collision course!',
            })
