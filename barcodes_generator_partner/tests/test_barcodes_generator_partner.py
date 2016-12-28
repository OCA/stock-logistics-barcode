# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today GRAP (http://www.grap.coop)
# Copyright (C) 2016-Today La Louve (http://www.lalouve.net)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class Tests(TransactionCase):
    """Tests for 'Barcodes Generate"""

    def setUp(self):
        super(Tests, self).setUp()
        self.partner_obj = self.env['res.partner']

    # Test Section
    def test_01_sequence_generation_partner(self):
        self.partner = self.partner_obj.browse(self.ref(
            'barcodes_generator_partner.res_partner_barcode'))
        self.partner.generate_barcode()
        self.assertEqual(
            self.partner.barcode_base, 1,
            "Incorrect base Generation (by sequence) for Partner.")
        self.assertEqual(
            self.partner.barcode, "0420000000013",
            "Barcode Generation (by sequence) for Partner."
            "Incorrect EAN13 Generated. Pattern : %s - Base : %s" % (
                self.partner.barcode_rule_id.pattern,
                self.partner.barcode_base))
