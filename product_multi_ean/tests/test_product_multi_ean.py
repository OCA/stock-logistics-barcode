# © 2016 Pedro M. Baeza
# © 2018 Xavier Jimenez (QubiQ)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase
from ..hooks import post_init_hook


class TestProductMultiEan(TransactionCase):
    def setUp(self):
        super(TestProductMultiEan, self).setUp()
        self.product = self.env['product.product'].create({
            'name': 'Test product',
        })
        self.valid_ean = '1234567890128'
        self.valid_ean2 = '0123456789012'

    def test_set_main_ean(self):
        self.product.barcode = self.valid_ean
        self.assertEqual(len(self.product.ean13_ids), 1)
        self.assertEqual(self.product.ean13_ids.name, self.product.barcode)

    def test_set_incorrect_ean(self):
        with self.assertRaises(Exception):
            self.product.barcode = '1234567890123'
        with self.assertRaises(Exception):
            self.product.ean13_ids = [(0, 0, {'name': '1234567890123'})]
        self.product.barcode = self.valid_ean
        # Insert duplicated EAN13
        with self.assertRaises(Exception):
            self.product.ean13_ids = [(0, 0, {'name': self.valid_ean})]

    def test_post_init_hook(self):
        self.env.cr.execute("""
            UPDATE product_product
            SET barcode = %s
            WHERE id = %s""", (self.valid_ean, self.product.id))
        post_init_hook(self.env.cr, self.registry)
        self.product.refresh()
        self.assertEqual(len(self.product.ean13_ids), 1)
        self.assertEqual(self.product.ean13_ids.name, self.valid_ean)

    def test_search(self):
        self.product.ean13_ids = [
            (0, 0, {'name': self.valid_ean}),
            (0, 0, {'name': self.valid_ean2})]
        products = self.product.search([('barcode', '=', self.valid_ean)])
        self.assertEqual(len(products), 1)
        self.assertEqual(products, self.product)
        products = self.product.search([('barcode', '=', self.valid_ean2)])
        self.assertEqual(len(products), 1)
        self.assertEqual(products, self.product)
