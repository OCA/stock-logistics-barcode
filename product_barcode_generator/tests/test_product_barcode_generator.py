# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Damien Crier
#    Copyright 2015 Camptocamp SA
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.tests import common


class TestProductBarcodeGenerator(common.TransactionCase):

    def setUp(self):
        super(TestProductBarcodeGenerator, self).setUp()
        self.sequence1 = self.env.ref(
            'product_barcode_generator.seq_ean13_sequence')
        if not self.sequence1.barcode_sequence:
            self.sequence1.barcode_sequence = True

        self.product_demo = self.env.ref('product.product_product_6')
        self.product_obj = self.env['product.product']

    def test_product_copy(self):
        self.product_demo.write({'barcode': False})
        self.product_demo.generate_ean13()
        new_product = self.env['product.product'].create({
            'name': 'Test product',
            'product_tmpl_id': self.product_demo.product_tmpl_id.id,
        })
        self.assertFalse(bool(new_product.barcode))
