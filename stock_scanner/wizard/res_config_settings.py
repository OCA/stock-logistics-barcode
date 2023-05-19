# © 2015 Laurent Mignon <laurent.mignon@acsone.eu>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models

ACTIVABLE_XML_IDS = [
    'stock_scanner.hardware_reset_user_id_on_timeout',
    'stock_scanner.scanner_scenario_login',
    'stock_scanner.scanner_scenario_logout',
]


class StockConfig(models.TransientModel):
    """Add options to configure login/logout on scanner"""
    _inherit = 'res.config.settings'

    is_login_enabled = fields.Boolean('Login/logout scenarii enabled')
    session_timeout_delay = fields.Integer('Session validity in seconds')

    def get_values(self):
        values = super().get_values()
        is_login_enabled = self.env.ref(ACTIVABLE_XML_IDS[0]).active
        session_timeout_delay = self.env.ref(
            'stock_scanner.hardware_scanner_session_timeout_sec').value

        values.update(
            is_login_enabled=is_login_enabled,
            session_timeout_delay=int(session_timeout_delay))

        return values

    def set_values(self):
        res = super().set_values()
        for xml_id in ACTIVABLE_XML_IDS:
            self.env.ref(xml_id).active = self.is_login_enabled

        self.env['ir.config_parameter'].set_param(
            'hardware_scanner_session_timeout', self.session_timeout_delay)

        return res
