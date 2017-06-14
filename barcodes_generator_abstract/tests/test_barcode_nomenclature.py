# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models
from odoo.tests import common
from odoo.exceptions import UserError


class BarcodeRule(models.Model):
    _inherit = 'barcode.rule'
    _name = 'barcode.rule'
    generate_model = fields.Selection(
        [('ir.model', 'IrModel')],
    )


class IrModel(models.Model):
    _name = 'ir.model'
    _inherit = ['ir.model', 'barcode.generate.mixin']
    barcode = fields.Char()


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
        model = cls.env[model_cls._name].with_context(todo=[])
        model._prepare_setup()
        model._setup_base(partial=False)
        model._setup_fields(partial=False)
        model._setup_complete()
        model._auto_init()
        model.init()
        model._auto_end()
        cls.test_model_record = cls.env['ir.model'].search([
            ('name', '=', model._name),
        ])
        return inst

    @classmethod
    def setUpClass(cls):
        super(TestBarcodeNomenclature, cls).setUpClass()
        cls.env.registry.enter_test_mode()
        cls._init_test_model(BarcodeRule)
        cls._init_test_model(IrModel)

    @classmethod
    def tearDownClass(cls):
        cls.env.registry.leave_test_mode()
        super(TestBarcodeNomenclature, cls).tearDownClass()

    def setUp(self):
        super(TestBarcodeNomenclature, self).setUp()
        self.nomenclature = self.env.ref(
            'barcodes.default_barcode_nomenclature',
        )
        self.rule = self.nomenclature.rule_ids.filtered(
            lambda r: r.pattern == '.*'
        )
        self.rule.write({
            'generate_model': 'ir.model',
            'pattern': 'MATCH-{NNNN}',
        })
        self.record = self.env['ir.model'].search([], limit=1)
        self.record.barcode = 'MATCH-1234'

    def test_find_by_barcode(self):
        """ It should find the correct record. """
        self.assertEqual(
            self.nomenclature.find_by_barcode(self.record.barcode),
            self.record,
        )

    def test_find_by_barcode_no_parse_match(self):
        """ It should return None if no matching barcode rule. """
        self.rule.pattern = 'NOMATCH-1234'
        self.assertEqual(
            self.nomenclature.find_by_barcode(self.record.barcode),
            None,
        )

    def test_find_by_barcode_no_generate_model(self):
        self.rule.generate_model = False
        self.assertEqual(
            self.nomenclature.find_by_barcode(self.record.barcode),
            None,
        )

    def test_form_action_for_barcode(self):
        """ It should return a dict. """
        res = self.nomenclature.get_form_action_for_barcode(
            self.record.barcode,
        )
        self.assertIsInstance(res, dict)

    def test_form_action_for_barcode_none(self):
        """ It should raise UserError on no match. """
        self.rule.pattern = 'NOMATCH-1234'
        with self.assertRaises(UserError):
            self.nomenclature.get_form_action_for_barcode(
                self.record.barcode,
            )
