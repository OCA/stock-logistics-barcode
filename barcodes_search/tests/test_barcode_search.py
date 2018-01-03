# coding: utf-8
# Copyright (C) 2017-Today GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class Tests(TransactionCase):
    """Tests barcodes_search module """

    def setUp(self):
        super(Tests, self).setUp()
        self.BarcodeSearch = self.env["barcode.search"]
        self.partner_with_barcode_id = self.ref(
            "barcodes_search.partner_with_barcode")
        self.BarcodeRule = self.env["barcode.rule"]
        # Add the key "price" (and the according rule)
        # because this key is added only if point of sale is installed
        self.BarcodeRule._fields["type"].selection.append(("price", "Price"))
        self.price_rule = self.BarcodeRule.create({
            "name": "Demo Price Rule Barcode",
            "barcode_nomenclature_id": self.ref(
                "barcodes.default_barcode_nomenclature"),
            "sequence": 1,
            "type": "price",
            "encoding": "ean13",
            "pattern": "23.....{NNNDD}",
        })

    # Test Section
    def test_search_single_result(self):
        res = self.BarcodeSearch.search_by_barcode("0419100000009")

        self.assertEqual(
            len(res), 1,
            "Searching a partner by it barcode should return one result")

        result = res[0]

        self.assertEqual(result["field"].model, "res.partner")
        self.assertEqual(result["field"].name, "barcode")
        self.assertEqual(result["record"].id, self.partner_with_barcode_id)

    def test_search_no_result(self):
        res = self.BarcodeSearch.search_by_barcode("112233445566778899")

        self.assertEqual(
            len(res), 0,
            "Searching an item by an inexisting barcode should not return"
            " any result")

    def test_search_many_result(self):
        res = self.BarcodeSearch.search_by_barcode("3057068106783")

        self.assertEqual(
            len(res), 2,
            "Searching a normal product by it barcode should return 2 result :"
            " the template and the variant")

    def test_search_price_barcode(self):
        res = self.BarcodeSearch.search_by_barcode("2391000005002")
        self.assertEqual(
            len(res), 1,
            "Searching a priced barcode should return a product.")

        result = res[0]
        self.assertEqual(result["extra_data"]["type"], "price")
        self.assertEqual(result["extra_data"]["value"], 5.0)
