# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class Tests(TransactionCase):
    """Tests 'Barcodes Generator for Products'"""

    def test_multi_barcodes_generator(self):
        barcode_rule_id = self.env["barcode.rule"].create(
            {
                "name": "Product Rule (Generated Barcode)",
                "type": "product",
                "sequence": 999,
                "encoding": "ean13",
                "pattern": "20.....{NNNDD}",
                "generate_type": "manual",
            }
        )
        product = self.env["product.product"].create(
            {
                "name": "Multi Barcodes Generator",
                "barcode_rule_id": barcode_rule_id.id,
                "barcode_base": 5,
            }
        )
        self.env["product.barcode"].create(
            {
                "product_id": product.id,
                "name": "1111111111111",
            }
        )
        product.generate_barcode()
        self.assertEqual(len(product.barcode_ids), 2)
