# Copyright 2021 Tecnativa - Carlos Roca
# Copyright 2023-Today GRAP (http://www.grap.coop)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.exceptions import UserError
from odoo.orm.model_classes import add_to_registry

from odoo.addons.base.tests.common import BaseCommon

from .models import BarcodeGeneratorUserFake, BarcodeRuleUserFake


class TestBarcodesGeneratorAbstract(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        add_to_registry(cls.registry, BarcodeGeneratorUserFake)
        add_to_registry(cls.registry, BarcodeRuleUserFake)
        test_models = ["res.users.tester", "barcode.rule"]

        cls.registry._setup_models__(cls.env.cr, test_models)
        cls.registry.init_models(cls.env.cr, test_models, {"models_to_check": True})
        cls.addClassCleanup(cls.registry.__delitem__, "res.users.tester")

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
                "generate_model": "res.users.tester",
            }
        )

        cls.user_fake = cls.env["res.users.tester"].create(
            {
                "name": "Test user",
                "login": "testing_01",
            }
        )

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
