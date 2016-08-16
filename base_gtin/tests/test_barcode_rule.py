# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.tests.common import TransactionCase


class TestBarcodeRule(TransactionCase):

    def setUp(self):
        super(TestBarcodeRule, self).setUp()
        self.model = self.env['barcode.rule']

    def test_encoding_selection_list(self):
        """ It should include EAN-14 in valid barcode types """
        self.assertIn(
            ('ean14', 'EAN-14'),
            self.model._encoding_selection_list(),
        )
