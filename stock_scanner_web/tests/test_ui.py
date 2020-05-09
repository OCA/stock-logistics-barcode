# © 2017 Jairo Llopis <jairo.llopis@tecnativa.com>
# © 2017 Angel Moya <angel.moya@pesol.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import odoo.tests


class TestUi(odoo.tests.HttpCase):

    def test_01_stock_scanner_web_tour(self):
        """Test frontend tour."""
        tour = "stock_scanner_web_tour"
        self.browser_js(
            "/stock_scanner_web",
            "odoo.__DEBUG__.services['web_tour.tour']"
            ".run('%s')" % tour,
            ready="odoo.__DEBUG__.services['web_tour.tour']"
                  ".tours.%s.ready" % tour,
            login="admin")
