# Copyright 2021 Sunflower IT
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.tests import common, tagged


@tagged("-at_install", "post_install")
class TestBarcodesMultilineUI(common.HttpCase):
    def setUp(self):
        super().setUp()

    def test_tour(self):
        self.start_tour("/web", "barcodes_multiline_tour", login="admin")
