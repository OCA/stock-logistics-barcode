# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.tests.common import HttpCase


class TestBarcodeParser(HttpCase):

    def setUp(self):
        super(TestBarcodeParser, self).setUp()

    def test_ui_web(self):
        self.phantom_js(
            "/web/tests?module=base_gtin",
            "",
            login="admin",
        )
