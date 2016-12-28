# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today GRAP (http://www.grap.coop)
# Copyright (C) 2016-Today La Louve (http://www.lalouve.net)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class Tests(TransactionCase):
    """Tests 'Barcodes Generator for Products'"""

    def setUp(self):
        super(Tests, self).setUp()
        self.template_obj = self.env['product.template']
        self.product_obj = self.env['product.product']

    # Test Section
    def test_01_manual_generation_template(self):
        self.template_mono = self.template_obj.browse(self.ref(
            'barcodes_generator_product.product_template_mono_variant'))
        self.assertEqual(
            self.template_mono.barcode, "2000050000003",
            "Incorrect Manual Barcode Generation for non varianted Template."
            " Pattern : %s - Base : %s" % (
                self.template_mono.barcode_rule_id.pattern,
                self.template_mono.barcode_base))

    def test_02_manual_generation_product(self):
        self.product_variant_1 = self.product_obj.browse(self.ref(
            'barcodes_generator_product.product_product_variant_1'))
        self.assertEqual(
            self.product_variant_1.barcode, "2010001000006",
            "Incorrect Manual Barcode Generation for varianted Product."
            " Pattern : %s - Base : %s" % (
                self.product_variant_1.barcode_rule_id.pattern,
                self.product_variant_1.barcode_base))
