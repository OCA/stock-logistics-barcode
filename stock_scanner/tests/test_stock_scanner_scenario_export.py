# Copyright 2017 SYLEAM Info Services
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import exceptions
from odoo.tests import common


class TestStockScannerScenarioExport(common.TransactionCase):
    def test_scenario_export(self):
        scenario_tested = self.env.ref("stock_scanner.scanner_scenario_tutorial")
        wiz = self.env["wizard.export.scenario"].create(
            {"scenario_ids": [(6, 0, [scenario_tested.id])]}
        )
        wiz.action_export()

        wiz = self.env["wizard.export.scenario"].create(
            {"scenario_ids": [(6, 0, [scenario_tested.id])], "is_copy": True}
        )
        wiz.action_export()
