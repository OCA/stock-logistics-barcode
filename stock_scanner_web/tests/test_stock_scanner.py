# -*- coding: utf-8 -*-
from openerp.tests import common


class TestStockScannerWeb(common.TransactionCase):

    def test_scenario_list(self):
        """Test the scenario list for web"""
        scenario_list = self.env['scanner.hardware'].with_context(
            {'stock_scanner_call_from_web': True}
        )._scenario_list()
        scanner_scenario_login = self.env.ref(
            'stock_scanner.scanner_scenario_login').name
        scanner_scenario_logout = self.env.ref(
            'stock_scanner.scanner_scenario_logout').name
        self.assertNotIn(scanner_scenario_login, scenario_list)
        self.assertNotIn(scanner_scenario_logout, scenario_list)
