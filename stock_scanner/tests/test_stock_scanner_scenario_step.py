# Copyright 2017 SYLEAM Info Services
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import exceptions
from odoo.tests import common
from odoo.tools.misc import mute_logger


class TestStockScannerScenarioStep(common.TransactionCase):
    def test_step_code_syntax(self):
        """ Should raise if the python code contains syntax errors """
        step = self.env.ref(
            'stock_scanner.'
            'scanner_scenario_step_sentinel_introduction')
        with self.assertRaises(exceptions.ValidationError):
            with mute_logger('stock_scanner'):
                step.python_code = 'function('
