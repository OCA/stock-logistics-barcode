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
                     website=True,
                     **kwargs):
        values = {}  # Reset the values.
        parameters = kwargs.copy()
        if 'debug' in parameters:
            parameters.pop('debug')
        if message == 'False':
            message = False
        if not message and parameters:
            message = kwargs
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
        step = scenario_step and int(scenario_step) or 0
        header = False
        lines = False
        if code == 'L':
            header = ''
            lines = []
            for line in result:
                if len(line) != 2 and line[0] != '|' and line[0] != '#':
                    lines.append({
                        'href': '/stock_scanner_web/%s/%s/action/%s' % (
                            terminal_number, step, line),
                        'label': line})
                elif len(line) != 2 and line[0] == '|':
                    header = line[1:]
                elif len(line) == 2 and line[0] != '|':
                    lines.append({
                        'href': '/stock_scanner_web/%s/%s/action?message=%s' %
                        (terminal_number, step, line[0]),
                        'label': line[1]})
                elif len(line) != 2 and line[0] == '#':
                    lines.append({
                        'href': False,
                        'label': line[1:]})
            header = header or message or _('Main Menu')
            lines = lines
        elif code in ['M', 'E', 'F', 'C', 'N', 'Q', 'T']:
            header = result[0]
            lines = result[1:]
        elif code == 'R':
            header = ''
            lines = result
        if code != 'W':
            if header and header[0] == '|':
                header = header[1:]
            result = {
                'header': header,
                'lines': lines
            }
        lang = request.env['res.lang'].search([('code', '=', user.lang)])
        values = {
            'code': code,
            'result': result,
            'value': value,
            'scenario': scenario,
            'step': step,
            'terminal_number': terminal_number,
            'show_numpad': scanner_hardware.show_numpad,
            'decimal_point': lang and lang.decimal_point or 'E'
        }
        if not message and action == 'reset':
            values['action'] = 'reset'
        return http.request.render('stock_scanner_web.scanner_call',
                                   values)
