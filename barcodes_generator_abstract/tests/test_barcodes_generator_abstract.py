# Copyright 2021 Tecnativa - Carlos Roca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo_test_helper import FakeModelLoader

from odoo.tests import TransactionCase


class TestBarcodesGeneratorAbstract(TransactionCase, FakeModelLoader):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.loader = FakeModelLoader(cls.env, cls.__module__)
        cls.loader.backup_registry()
        from .models import BarcodeGeneratorUserFake, BarcodeRuleUserFake

        cls.loader.update_registry(
            (
                BarcodeGeneratorUserFake,
                BarcodeRuleUserFake,
            )
        )
        cls.barcode_rule_fake = cls.env["barcode.rule"].create(
            {
                "name": "User rule",
                "barcode_nomenclature_id": cls.env.ref(
                    "barcodes.default_barcode_nomenclature"
                ).id,
                "type": "user",
                "sequence": 999,
                "encoding": "ean13",
                "pattern": "20.....{NNNDD}",
                "generate_type": "manual",
                "generate_model": "res.users",
            }
        )
        cls.user_fake = cls.env["res.users"].create(
            {
                "name": "Test user",
                "login": "testing_01",
                "barcode_rule_id": cls.barcode_rule_fake.id,
                "barcode_base": 10,
            }
        )
        cls.user_fake.generate_barcode()

    @classmethod
    def tearDownClass(cls):
        cls.loader.restore_registry()
        super().tearDownClass()

    def test_generate_sequence(self):
        self.assertEqual(
            self.user_fake.barcode,
            "2000010000005",
        )
