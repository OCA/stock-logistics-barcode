# Copyright 2015 Therp BV (<http://therp.nl>)
# Copyright 2016 ACSONE SA/NV (<http://acsone.eu>)
# Copyright 2021 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import exceptions
from odoo.tests import common

VALID_EAN8_CODES = [
    "40123455",
    "04210009",
]
VALID_UPC_CODES = [
    "012345678905",
    "080047440694",
    "123456789012",
]
VALID_EAN13_CODES = [
    "2000021262157",
]


class TestProductGtin(common.TransactionCase):
    def setUp(self):
        super().setUp()
        self.barcode_mixin = self.env["barcode.gtin_check.mixin"]
        self.company = self.env.ref("base.main_company")
        self.company.write(
            {
                "check_code_type_ean8": True,
                "check_code_type_isbn10": True,
                "check_code_type_upc": True,
                "check_code_type_ean13": True,
            }
        )
        self.product = self.env["product.product"].create(
            {"name": "Test product", "company_id": self.company.id}
        )

    def test_check_ean8(self):
        for code in VALID_EAN8_CODES:
            self.assertTrue(self.barcode_mixin._check_ean8(code))
        # Ean8 should not accept Ean13
        for code in VALID_EAN13_CODES:
            self.assertFalse(self.barcode_mixin._check_ean8(code))
        # Ean8 should not accept UPC
        for code in VALID_UPC_CODES:
            self.assertFalse(self.barcode_mixin._check_ean8(code))

    def test_check_upc(self):
        for code in VALID_UPC_CODES:
            self.assertTrue(self.product._check_upc(code))
        # Ean8 codes should not be valid for UPC
        for code in VALID_EAN8_CODES:
            self.assertFalse(self.barcode_mixin._check_upc(code))
        # Ean13 codes should not be valid for UPC
        for code in VALID_EAN13_CODES:
            self.assertFalse(self.barcode_mixin._check_upc(code))

    def test_check_ean13(self):
        for code in VALID_EAN13_CODES:
            self.assertTrue(self.barcode_mixin._check_ean13(code))
        # Ean13 should not accept ean8
        for code in VALID_EAN8_CODES:
            self.assertFalse(self.barcode_mixin._check_ean13(code))
        # Ean13 should not accept UPC
        for code in VALID_UPC_CODES:
            self.assertFalse(self.barcode_mixin._check_ean13(code))

    def test_wrong_upc_codes(self):
        self.assertFalse(self.product._check_upc(""))
        # test string
        self.assertFalse(self.product._check_upc("odoo_oca"))
        # less than 12 numbers
        self.assertFalse(self.product._check_upc("12345678901"))
        # 12 random numbers
        self.assertFalse(self.product._check_upc("123456789013"))
        # more than 12 numbers
        self.assertFalse(self.product._check_upc("12345678980123"))

    def test_wrong_ean8_codes(self):
        self.assertFalse(self.barcode_mixin._check_ean8(""))
        # test string
        self.assertFalse(self.barcode_mixin._check_ean8("odoo_oca"))
        # less than 8 numbers
        self.assertFalse(self.barcode_mixin._check_ean8("1234567"))
        # 8 random numbers
        self.assertFalse(self.barcode_mixin._check_ean8("12345678"))
        self.assertFalse(self.barcode_mixin._check_ean8("82766678"))
        # 9 numbers
        self.assertFalse(self.barcode_mixin._check_ean8("123456789"))

    def test_wrong_ean13_codes(self):
        self.assertFalse(self.barcode_mixin._check_ean13(""))
        # test string
        self.assertFalse(self.barcode_mixin._check_ean8("odoo_oca_sflx"))
        # less than 13 numbers
        self.assertFalse(self.barcode_mixin._check_ean13("123456789012"))
        # 13 random numbers
        self.assertFalse(self.barcode_mixin._check_ean13("1234567890123"))
        self.assertFalse(self.barcode_mixin._check_ean13("1234514728123"))
        # 14 numbers
        self.assertFalse(self.barcode_mixin._check_ean13("12345147281234"))

    def test_dicts_check_exist(self):
        """Check if the dicts _DICT_CHECK_CODE_TYPE
        and _DICT_CHECK_FUNCTIONS exist."""
        self.assertTrue(self.barcode_mixin._DICT_CHECK_CODE_TYPE)
        self.assertTrue(self.barcode_mixin._DICT_CHECK_FUNCTIONS)

    def test_product_constrains(self):
        self.product.write({"barcode": "1234"})
        self.assertEquals(self.product.barcode, "1234")
        with self.assertRaises(exceptions.ValidationError):
            self.product.write({"barcode": "1234567890123"})
        self.product.write({"barcode": "2000021262157"})
        self.assertEquals(self.product.barcode, "2000021262157")

    def test_product_constrains_without_company_checks(self):
        self.company.write(
            {
                "check_code_type_ean8": False,
                "check_code_type_isbn10": False,
                "check_code_type_upc": False,
                "check_code_type_ean13": False,
            }
        )
        # Wrong ean8
        self.product.write({"barcode": "12345678"})
        self.assertEquals(self.product.barcode, "12345678")
        # Wrong isbn
        self.product.write({"barcode": "1234567890"})
        self.assertEquals(self.product.barcode, "1234567890")
        # Wrong upc
        self.product.write({"barcode": "123456789012"})
        self.assertEquals(self.product.barcode, "123456789012")
        # Wrong ean13
        self.product.write({"barcode": "1234567890123"})
        self.assertEquals(self.product.barcode, "1234567890123")
