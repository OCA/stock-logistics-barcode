# -*- coding: utf-8 -*-
# © 2017 Jairo Llopis <jairo.llopis@tecnativa.com>
# © 2017 Angel Moya <angel.moya@pesol.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.tests.common import HttpCase


class UICase(HttpCase):

    def test_stock_scanner_web(self):
        """Test frontend tour."""
        self.phantom_js(
            url_path="/stock_scanner_web",
            code="odoo.__DEBUG__.services['web.Tour']"
                 ".run('stock_scanner_web', 'test')",
            ready="odoo.__DEBUG__.services['web.Tour']"
                  ".tours.stock_scanner_web",
            login="admin")
