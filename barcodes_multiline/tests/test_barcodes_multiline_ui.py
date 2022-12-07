# -*- coding: utf-8 -*-
# Copyright 2021 Sunflower IT
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.tests.common import HttpCase, at_install, post_install


@at_install(False)
@post_install(True)
class TestBarcodesMultilineUI(HttpCase):

    def test_barcodes_multiline_tour(self):
        self.phantom_js(
            "/web",
            "odoo.__DEBUG__.services['web_tour.tour'].run('barcodes_multiline.tour')",
            "odoo.__DEBUG__.services['web_tour.tour']"
            ".tours['barcodes_multiline.tour'].ready",
            login="admin"
        )
