# Copyright 2021 Tecnativa - Carlos Roca
# Copyright 2023-Today GRAP (http://www.grap.coop)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo_test_helper import FakeModelLoader

from odoo.exceptions import UserError

from odoo.addons.base.tests.common import BaseCommon


class TestBarcodesGeneratorAbstract(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def setUp(self):
        super().setUp()
        self.loader = FakeModelLoader(self.env, self.__module__)
        self.loader.backup_registry()
        from .models import BarcodeGeneratorUserFake, BarcodeRuleUserFake

        self.loader.update_registry(
            (
                BarcodeGeneratorUserFake,
                BarcodeRuleUserFake,
            )
        )
        self.barcode_rule_fake = self.env["barcode.rule"].create(
            {
                "name": "User rule",
                "barcode_nomenclature_id": self.env.ref(
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
        self.user_fake = self.env["res.users"].create(
            {
                "name": "Test user",
                "login": "testing_01",
            }
        )

    def tearDown(self):
        self.loader.restore_registry()
        super().tearDown()

    def test_generate_sequence_manually(self):
        self.user_fake.barcode_rule_id = self.barcode_rule_fake
        self.assertFalse(self.user_fake.barcode_base)
        self.assertFalse(self.user_fake.barcode)

        with self.assertRaises(UserError):
            self.user_fake.generate_base()

        self.user_fake.generate_barcode()
        self.assertEqual(
            self.user_fake.barcode,
            "2000000000008",
        )
        self.user_fake.barcode_base = 10
        self.user_fake.generate_barcode()
        self.assertEqual(
            self.user_fake.barcode,
            "2000010000005",
        )

    def test_generate_sequence_sequence(self):
        self.barcode_rule_fake.generate_type = "sequence"
        self.assertTrue(self.barcode_rule_fake.sequence_id)

        self.user_fake.barcode_rule_id = self.barcode_rule_fake
        self.assertFalse(self.user_fake.barcode_base)
        self.assertFalse(self.user_fake.barcode)

        self.user_fake.generate_base()
        self.assertEqual(self.user_fake.barcode_base, 1)
        self.assertFalse(self.user_fake.barcode)

        self.user_fake.generate_barcode()
        self.assertEqual(self.user_fake.barcode, "2000001000007")

        self.user_fake.generate_base()
        self.assertEqual(self.user_fake.barcode_base, 2)
        self.user_fake.generate_barcode()
        self.assertEqual(self.user_fake.barcode, "2000002000006")

    def test_generate_sequence_sequence_automate(self):
        self.barcode_rule_fake.write(
            {
                "generate_type": "sequence",
                "generate_automate": True,
            }
        )
        self.assertTrue(self.barcode_rule_fake.sequence_id)

        self.user_fake.barcode_rule_id = self.barcode_rule_fake
        self.assertEqual(self.user_fake.barcode_base, 1)
        self.assertEqual(self.user_fake.barcode, "2000001000007")
