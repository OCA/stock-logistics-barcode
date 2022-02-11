# Copyright 2022 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import common


@common.tagged("post_install", "-at_install")
class TestStockBarcodesGS1(common.TransactionCase):
    def setUp(self):
        super().setUp()
        self.company = self.env.user.company_id
        self.product_tracking = self.env["product.product"].create(
            {
                "name": "Product test with lot tracking",
                "type": "product",
                "tracking": "lot",
                "barcode": "8433281006850",
                "packaging_ids": [
                    (
                        0,
                        0,
                        {"name": "Box 5 Units", "qty": 5.0, "barcode": "5420008510489"},
                    )
                ],
            }
        )
        self.lot_1 = self.env["stock.production.lot"].create(
            {
                "name": "8411822222568",
                "product_id": self.product_tracking.id,
                "company_id": self.company.id,
            }
        )

    def test_barcode(self):
        my_barcode = self.lot_1.encode_gs1()
        decoded_barcode = self.env["gs1_barcode"].decode(my_barcode)
        product = self.env["product.product"].search(
            [("barcode", "=", decoded_barcode["01"])], limit=1
        )
        self.assertEqual(product, self.product_tracking)
        self.assertEqual(
            self.env["stock.production.lot"].search(
                [("product_id", "=", product.id), ("name", "=", decoded_barcode["10"])]
            ),
            self.lot_1,
        )
