# © 2011 Sylvain Garancher <sylvain.garancher@syleam.fr>
# © 2017 Angel Moya <angel.moya@pesol.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, api, fields


class ScannerHardware(models.Model):
    _inherit = 'scanner.hardware'

    show_numpad = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No'),
    ], string='Show Numpad')

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
            search_domain = [
                ('parent_id', '=', parent_id)]
            if self.warehouse_id:
                search_domain += [
                    '|',
                    ('warehouse_ids', 'in', [self.warehouse_id.id])]
            search_domain.append(
                ('warehouse_ids', '=', False))
            scanner_scenarios = scanner_scenario_obj.search(
                search_domain)
            scenario_names = [scenario.name for scenario in
                              scanner_scenarios if scenario not in (
                                  scanner_scenario_login,
                                  scanner_scenario_logout)]
            return scenario_names
        else:
            return super(ScannerHardware, self)._scenario_list(
                parent_id=parent_id)
