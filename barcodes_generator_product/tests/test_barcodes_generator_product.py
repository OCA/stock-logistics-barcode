# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today GRAP (http://www.grap.coop)
# Copyright (C) 2016-Today La Louve (http://www.lalouve.net)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.tests.common import TransactionCase


class Tests(TransactionCase):
    """Tests 'Barcodes Generator for Products'"""

    def setUp(self):
        super(Tests, self).setUp()
        self.template_obj = self.env['product.template']
        self.product_obj = self.env['product.product']
        self.barcode_rule_obj = self.env['barcode.rule']
        
        self.attribute = self.env['product.attribute'].create({
            'name': 'Test Attribute',
        })
        self.value1 = self.env['product.attribute.value'].create({
            'name': 'Value 1',
            'attribute_id': self.attribute.id,
        })
        self.value2 = self.env['product.attribute.value'].create({
            'name': 'Value 2',
            'attribute_id': self.attribute.id,
        })
        self.barcode_product_rule = self.barcode_rule_obj.create({
            'name': 'Test product rule',
            'barcode_nomenclature_id': self.env.ref(
                'barcodes.default_barcode_nomenclature').id,
            'type': 'product',
            'sequence': 1000,
            'encoding': 'ean13',
            'pattern': '20.....{NNNDD}',
            'generate_type': 'manual',
            'generate_model': 'product.product',
        })

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

    def test_03_propagate_rule_to_variants(self):
        template = self.template_obj.create({
            'name': 'Product - template - Test',
            'barcode_rule_id': self.barcode_product_rule.id,
            'attribute_line_ids': [
                (0, 0, {
                    'attribute_id': self.attribute.id,
                    'value_ids': [(6, 0, [self.value1.id, self.value2.id])]
                })],
        })
        rule = template.mapped('product_variant_ids.barcode_rule_id')
        self.assertEqual(len(rule), 1)
