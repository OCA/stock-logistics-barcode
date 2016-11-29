# -*- coding: utf-8 -*-
# Copyright 2016 Angel Moya <http://angelmoya.es>
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
        '/scanner_call',
        '/scanner_call/<string:terminal_number>',
        '/scanner_call/<string:terminal_number>/<string:action>',
        '/scanner_call/<string:terminal_number>/<string:action>/'
        '<string:message>',
    ], website=True, auth='user')
    def scanner_call(self,
                     terminal_number='',
                     action='',
                     message=False,
                     type='http',
                     auth='public',
                     website=True):
        values = {}
        if message == 'False':
            message = False

        scanner_hardware = request.env['scanner.hardware']
        try:
            user = request.env.user.browse(request.uid)
            if terminal_number and not allowed_hardware(user, terminal_number):
                values = {
                    'code': 'E',
                    'result':
                        _('Hardware {} not allowed for user {}.').format(
                            terminal_number, user.name)
                }
                return http.request.render(
                    'stock_scanner_web.hardware_select',
                    values)
            terminal_list = []
            if not terminal_number:
                for hardware in user.scanner_hardware_ids:
                    terminal_list.append(hardware.code)
                if terminal_list:
                    values = {
                        'code': 'L',
                        'result': terminal_list
                    }
                else:
                    values = {
                        'code': 'N',
                        'result': _("You do not have any hardware allowed. "
                                    "Please contact your administrator.")
                    }
                return http.request.render('stock_scanner_web.hardware_select',
                                           values)

            (code, result, value) = scanner_hardware.with_context(
                stock_scanner_call_from_web=True).scanner_call(
                terminal_number,
                action,
                message)
            scenario = scanner_hardware.scanner_check(terminal_number)
            values = {
                'code': code,
                'result': result,
                'value': value,
                'scenario': scenario,
                'terminal_number': terminal_number
            }
            return http.request.render('stock_scanner_web.scanner_call',
                                       values)
        except Exception as e:
            values = {
                'code': 'E',
                'result':
                    _('Error: %s') % e.message
            }
            return http.request.render(
                'stock_scanner_web.hardware_select',
                values)
