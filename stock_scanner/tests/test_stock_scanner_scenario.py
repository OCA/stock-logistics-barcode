# Copyright 2017 SYLEAM Info Services
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import exceptions
from odoo.tests import common


class TestStockScannerScenario(common.TransactionCase):
    def test_recursive_scenarios(self):
        """ Should raise if the scenario is recursive """
        parent_scenario = self.env.ref(
            'stock_scanner.scanner_scenario_tutorial')
        child_scenario = self.env.ref(
            'stock_scanner.scanner_scenario_sentinel')
        with self.assertRaises(exceptions.ValidationError):
            parent_scenario.parent_id = child_scenario
