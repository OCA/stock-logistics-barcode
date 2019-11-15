# Copyright (C) 2019 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import http
from odoo.http import request


class Home(http.Controller):

    @http.route('/mobile_app_picking', type='http', auth="none")
    def index(self, s_action=None, db=None, **kw):
        return http.local_redirect(
            '/mobile_app_picking/static/www/index.html',
            query=request.params)
