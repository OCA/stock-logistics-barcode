# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models
from odoo.tests import common


class BarcodeRule(models.Model):
    _inherit = 'barcode.rule'
    generate_model = fields.Selection(
        [('product.template', 'Product Template')],
    )


class TestBarcodeNomenclature(common.SavepointCase):

    @classmethod
    def _init_test_model(cls, model_cls):
        """ It builds a model from model_cls in order to test abstract models.
        Note that this does not actually create a table in the database, so
        there may be some unidentified edge cases.
        Args:
            model_cls (odoo.models.BaseModel): Class of model to initialize
        Returns:
            model_cls: Instance
        """
        registry = cls.env.registry
        cr = cls.env.cr
        inst = model_cls._build_model(registry, cr)
        model = cls.env[model_cls._inherit].with_context(todo=[])
        model._prepare_setup()
        model._setup_base(partial=False)
        model._setup_fields(partial=False)
        model._setup_complete()
        model._auto_init()
        model.init()
        model._auto_end()
        cls.test_model_record = cls.env['ir.model'].search([
            ('name', '=', model._inherit),
        ])
        return inst

    @classmethod
    def setUpClass(cls):
        super(TestBarcodeNomenclature, cls).setUpClass()
        cls.env.registry.enter_test_mode()
        cls._init_test_model(BarcodeRule)
        cls.test_model = cls.env[BarcodeRule._inherit]

    def setUp(self):
        super(TestBarcodeNomenclature, self).setUp()
        self.nomenclature = self.env.ref(
            'barcodes.default_barcode_nomenclature',
        )
        self.rule = self.nomenclature.rule_ids.filtered(
            lambda r: r.pattern == '.*'
        )
        self.rule.generate_model = 'product.template'
        self.product = self.env['product.template'].search([], limit=1)
        self.product.barcode = 'MATCH-12123234324'

    def test_find_by_barcode(self):
        """ It should find the correct record. """
        self.assertEqual(
            self.nomenclature.find_by_barcode(self.product.barcode),
            self.product,
        )

    def test_find_by_barcode_no_parse_match(self):
        """ It should return None if no matching barcode rule. """
        self.rule.pattern = 'NOMATCH'
        self.assertEqual(
            self.nomenclature.find_by_barcode(self.product.barcode),
            None,
        )

    def test_find_by_barcode_no_generate_model(self):
        self.rule.generate_model = False
        self.assertEqual(
            self.nomenclature.find_by_barcode(self.product.barcode),
            None,
        )
