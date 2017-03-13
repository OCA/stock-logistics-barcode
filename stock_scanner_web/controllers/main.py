# -*- coding: utf-8 -*-
# Copyright 2016 Eficent Business and IT Consulting Services, S.L.
# <http://www.eficent.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import http
from openerp.http import request
from openerp import _


def allowed_hardware(user, t_num):
    allowed = False
    for hardware in user.scanner_hardware_ids:
        if t_num == hardware.code:
            allowed = True
    return allowed


class ScannerWeb(http.Controller):
    @http.route([
        '/stock_scanner_web',
        '/stock_scanner_web/<string:terminal_number>',
        '/stock_scanner_web/<string:terminal_number>/<string:scenario_step>',
        '/stock_scanner_web/<string:terminal_number>/<string:scenario_step>'
        '/<string:action>/',
        '/stock_scanner_web/<string:terminal_number>/<string:scenario_step>/'
        '<string:action>/<string:message>/'
    ], type='http', auth='user')
    def scanner_call(self,
                     terminal_number='',
                     action='',
                     message=False,
                     scenario_step=False,
                     type='http',
                     auth='public',
                     website=True):
        values = {}  # Reset the values.
        if message == 'False':
            message = False
        # Determine the correct hardware:
        scanner_hardware = False
        user = request.env.user
        if terminal_number:
            if not allowed_hardware(user, terminal_number):
                values = {
                    'result':
                        _('Hardware {} not allowed for user {}.').format(
                            terminal_number, user.name)
                }
                return http.request.render(
                    'stock_scanner_web.hardware_select',
                    values)

        else:
            terminal_list = user.scanner_hardware_ids.mapped('code')
            if terminal_list and len(terminal_list) > 1:
                values = {
                    'code': 'L',
                    'result': terminal_list
                }
                return http.request.render(
                    'stock_scanner_web.hardware_select',
                    values)

            elif terminal_list and len(terminal_list) == 1:
                terminal_number = terminal_list[0]
            elif not terminal_list:
                values = {
                    'code': 'N',
                    'result': _("You do not have any hardware allowed. "
                                "Please contact your administrator.")
                }
                return http.request.render(
                    'stock_scanner_web.hardware_select',
                    values)

        # Now we have a valid hardware.
        scanner_hardware = request.env['scanner.hardware'].search(
            [('code', '=', terminal_number)])
        if not scanner_hardware:
            values = {
                'code': 'N',
                'result': _("No valid terminal.")
            }
            return http.request.render(
                'stock_scanner_web.hardware_select',
                values)

        if not message and action == 'reset':
            scanner_hardware.empty_scanner_values()
        try:
            (code, result, value) = scanner_hardware.with_context(
                stock_scanner_call_from_web=True).scanner_call(
                terminal_number,
                action,
                message)
        except Exception as e:
            values = {
                'result':
                    _('Error: %s') % e.message
            }
            return http.request.render(
                'stock_scanner_web.error_message',
                values)

        try:
            scenario = scanner_hardware.scanner_check(terminal_number)
        except Exception as e:
            values = {
                'result':
                    _('Error: %s') % e.message
            }
            return http.request.render(
                'stock_scanner_web.error_message',
                values)

        scenario_step = request.env['scanner.hardware'].\
            search([('code', '=', terminal_number)]).step_id
        if not scenario_step:
            scenario_step = 0
        values = {
            'code': code,
            'result': result,
            'value': value,
            'scenario': scenario,
            'step': int(scenario_step),
            'terminal_number': terminal_number
        }
        if not message and action == 'reset':
            values['action'] = 'reset'
        return http.request.render('stock_scanner_web.scanner_call',
                                   values)
