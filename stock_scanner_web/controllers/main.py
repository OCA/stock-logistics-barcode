# -*- coding: utf-8 -*-
# Copyright 2016 Angel Moya <http://angelmoya.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import http
from openerp.http import request


class ScannerWeb(http.Controller):

    @http.route([
        '/scanner_call/<string:terminal_number>',
        '/scanner_call/<string:terminal_number>/<string:action>',
        '/scanner_call/<string:terminal_number>/<string:action>/<string:message>',
    ], website=True)
    def scanner_call(self,
                     terminal_number='',
                     action='',
                     message=False,
                     type='http',
                     auth='public',
                     website=True):
        scanner_hardware = request.env()['scanner.hardware'].sudo()
        values = {}
        try:
            action = int(action)
        except Exception as e:
            pass
        (code, result, value) = scanner_hardware.scanner_call(
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
        return http.request.render('stock_scanner_web.scanner_call', values)
