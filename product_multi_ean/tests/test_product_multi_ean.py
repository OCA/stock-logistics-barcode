# © 2016 Pedro M. Baeza
# © 2018 Xavier Jimenez (QubiQ)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from psycopg2 import IntegrityError

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase, at_install, post_install, Form
from odoo.tools import mute_logger
from ..hooks import post_init_hook


@at_install(False)
@post_install(True)
class TestProductMultiEan(TransactionCase):
    def setUp(self):
        super(TestProductMultiEan, self).setUp()
        # Product 1
        self.product = self.env['product.product']
        self.product_1 = self.product.create({
            'name': 'Test product 1',
        })
        self.valid_ean_1 = '1234567890128'
        self.valid_ean2_1 = '0123456789012'
        # Product 2
        self.product_2 = self.product.create({
            'name': 'Test product 2',
        })
        self.valid_ean_2 = '9780471117094'
        self.valid_ean2_2 = '4006381333931'

    def test_set_main_ean(self):
        self.product_1.barcode = self.valid_ean_1
        self.assertEqual(len(self.product_1.ean13_ids), 1)
        self.assertEqual(self.product_1.ean13_ids.name, self.product_1.barcode)

    def test_set_incorrect_ean(self):
        self.product_1.barcode = self.valid_ean_1
        # Insert duplicated EAN13
        with self.assertRaises(Exception):
            self.product_1.ean13_ids = [(0, 0, {'name': self.valid_ean_1})]

    def test_post_init_hook(self):
        self.env.cr.execute("""
            UPDATE product_product
            SET barcode = %s
            WHERE id = %s""", (self.valid_ean_1, self.product_1.id))
        post_init_hook(self.env.cr, self.registry)
        self.product_1.refresh()
        self.assertEqual(len(self.product_1.ean13_ids), 1)
        self.assertEqual(self.product_1.ean13_ids.name, self.valid_ean_1)

    def test_search(self):
        self.product_1.ean13_ids = [
            (0, 0, {'name': self.valid_ean_1}),
            (0, 0, {'name': self.valid_ean2_1})]
        self.product_2.ean13_ids = [
            (0, 0, {'name': self.valid_ean_2}),
            (0, 0, {'name': self.valid_ean2_2})]
        products = self.product.search([('barcode', '=', self.valid_ean_1)])
        self.assertEqual(len(products), 1)
        self.assertEqual(products, self.product_1)
        products = self.product.search([('barcode', '=', self.valid_ean2_1)])
        self.assertEqual(len(products), 1)
        self.assertEqual(products, self.product_1)
        products = self.product.search(
            ['|', ('barcode', '=', self.valid_ean2_1),
             ('barcode', '=', self.valid_ean2_2)])
        self.assertEqual(len(products), 2)

    def _assign_barcode(self, product, barcode):
        if product._name == 'product.template':
            product_form = Form(product)
            product_form.barcode = barcode
            product = product_form.save()
        elif product._name == 'product.product':
            # Barcode is readonly in Product Variant view
            product.ean13_ids = [
                (0, 0, {
                    'name': barcode,
                }),
            ]
        return product

    def test_duplicate(self):
        """
        Two products with same EAN cannot exist.
        """
        # Arrange: one EAN and two different products
        ean = self.valid_ean_1
        product = self.product_1
        other_product = self.product_2
        self.assertNotEqual(product, other_product)

        # Act: assign the same EAN to both products
        self._assign_barcode(product, ean)

        with self.assertRaises(ValidationError) as ve:
            self._assign_barcode(other_product, ean)

        exc_message = ve.exception.args[0]

        # Assert: Cannot assign EAN to second product
        self.assertIn(ean, exc_message)
        self.assertIn(product.name, exc_message)
        self.assertIn('already exists', exc_message)

    def test_duplicate_archived(self):
        """
        Two products with same EAN can exist if one of them is archived.
        """
        # Arrange: one EAN and two different products
        ean = self.valid_ean_1
        product = self.product_1
        other_product = self.product_2
        self.assertNotEqual(product, other_product)
        # Assign the EAN to one product and archive it
        self._assign_barcode(product, ean)
        product.toggle_active()

        # Act: Assign the EAN to the other product and no error is raised
        self._assign_barcode(other_product, ean)

        # Additional check: Reactivating the product is blocked.
        # Here the constraint is not raised simply
        # because barcode unique constraint in module 'product' is raised first.
        with self.assertRaises(IntegrityError) as ve, \
                mute_logger('odoo.sql_db'):
            product.toggle_active()
        exc_message = ve.exception.args[0]
        self.assertIn(ean, exc_message)
        self.assertIn('already exists', exc_message)

    def test_duplicate_template_archived(self):
        """
        Two product templates with same EAN can exist if one of them is archived.
        """
        # Arrange: one EAN and two different products
        ean = self.valid_ean_1
        template = self.product_1.product_tmpl_id
        other_template = self.product_2.product_tmpl_id
        self.assertNotEqual(template, other_template)
        # Assign the EAN to one product and archive it
        self._assign_barcode(template, ean)
        template.toggle_active()

        # Act: Assign the EAN to the other product and no error is raised
        self._assign_barcode(other_template, ean)

        # Additional check: Reactivating the product is blocked.
        # Here the constraint is not raised simply
        # because barcode unique constraint in module 'product' is raised first.
        with self.assertRaises(IntegrityError) as ve, \
                mute_logger('odoo.sql_db'):
            template.toggle_active()
        exc_message = ve.exception.args[0]
        self.assertIn(ean, exc_message)
        self.assertIn('already exists', exc_message)
