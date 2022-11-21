# Copyright 2021 Tecnativa - Carlos Roca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo_test_helper import FakeModelLoader

from odoo.tests import SavepointCase


class TestBarcodesGeneratorAbstract(SavepointCase, FakeModelLoader):
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
        cls.sequence1 = cls.env["ir.sequence"].create(
            {
                "name": "First sequence",
                "last_number": 1,
                "number_next": 1,
                "padding": 5,
            }
        )
        cls.sequence2 = cls.env["ir.sequence"].create(
            {
                "name": "Second sequence",
                "last_number": 4,
                "number_next": 4,
                "padding": 5,
            }
        )
        cls.barcode_rule_fake_many_sequences = cls.env["barcode.rule"].create(
            {
                "name": "User many sequences rule",
                "barcode_nomenclature_id": cls.env.ref(
                    "barcodes.default_barcode_nomenclature"
                ).id,
                "type": "user",
                "sequence": 1000,
                "encoding": "ean13",
                "pattern": "21.....{NNNDD}",
                "generate_type": "many_sequences",
                "generate_model": "res.users",
                "number_of_sequences_todo": 2,
                "sequence_id": cls.sequence1.id,
                "sequences_ids": [cls.sequence1.id, cls.sequence2.id],
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
        cls.user_fake_many_sequences = cls.env["res.users"].create(
            {
                "name": "Test Many sequences user",
                "login": "testing_02",
                "barcode_rule_id": cls.barcode_rule_fake_many_sequences.id,
            }
        )
        cls.user_fake_many_sequences_2 = cls.env["res.users"].create(
            {
                "name": "Test Many sequences user 2",
                "login": "testing_03",
                "barcode_rule_id": cls.barcode_rule_fake_many_sequences.id,
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

    def test_generate_barcode_with_many_sequences(self):
        """This test assigns two barcodes to different users,
        supporting a change between rule sequences
        barcode generation.
        """
        self.user_fake_many_sequences.generate_base()
        self.user_fake_many_sequences.generate_barcode()
        self.assertEqual(
            self.user_fake_many_sequences.barcode,
            "2100001000004",
        )
        self.assertEqual(
            self.barcode_rule_fake_many_sequences.sequence_id.name,
            "First sequence",
        )
        self.user_fake_many_sequences_2.generate_base()
        self.user_fake_many_sequences_2.generate_barcode()
        self.assertEqual(
            self.user_fake_many_sequences_2.barcode,
            "2100004000001",
        )
        self.assertEqual(
            self.barcode_rule_fake_many_sequences.sequence_id.name,
            "Second sequence",
        )
