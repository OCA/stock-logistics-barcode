# Copyright 2024 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

from odoo_test_helper import FakeModelLoader

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestBarcodeValidationMixin(TransactionCase, FakeModelLoader):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.loader = FakeModelLoader(cls.env, cls.__module__)
        cls.loader.backup_registry()
        from .models import TestModelFake

        cls.loader.update_registry((TestModelFake,))
        cls.company = cls.env["res.company"].create({"name": "test company"})

    @classmethod
    def tearDownClass(cls):
        cls.loader.restore_registry()
        super().tearDownClass()

    @classmethod
    def toggle_barcode_validation(cls, value):
        cls.company.write(
            {
                "barcode_validation_upca": value,
                "barcode_validation_ean8": value,
                "barcode_validation_ean13": value,
                "barcode_validation_code128": value,
                "barcode_validation_datamatrix": value,
                "barcode_validation_qrcode": value,
            }
        )

    def test_barcode_validation(self):
        """Validate barcode when record is created/updated."""
        self.toggle_barcode_validation(True)
        with self.assertRaises(ValidationError):
            self.env["test.model"].with_company(self.company).create(
                {"name": "Test Model", "barcode": "123Ç"}
            )
        self.toggle_barcode_validation(False)
        test_record = (
            self.env["test.model"]
            .with_company(self.company)
            .create({"name": "Test Model", "barcode": "123Ç"})
        )
        self.assertEqual(test_record.barcode, "123Ç")
        self.toggle_barcode_validation(True)
        with self.assertRaises(ValidationError):
            test_record.write({"barcode": "123ÇÇ}"})
        self.toggle_barcode_validation(False)
        test_record.write({"barcode": "123ÇÇ}"})
