# Copyright 2026 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.tests import Form, TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestNewPackaging(TransactionCase):
    def test_confirm_packaging(self):
        product = self.env["product.product"].create({"name": "Packaged product"})
        action = self.env.ref(
            "stock_barcodes.stock_barcodes_action_inventory"
        ).open_action()
        scan = self.env[action["res_model"]].browse(action["res_id"])
        wizard_model = self.env["wiz.stock.barcodes.new.packaging"].with_context(
            active_model=scan._name, active_id=scan.id
        )
        with Form(wizard_model) as form:
            form.product_id = product
            form.name = "Box"
            form.barcode = "TEST-BOX"
        wizard = form.record
        result = wizard.confirm()
        self.assertEqual(result["res_id"], scan.id)
        self.assertEqual(scan.packaging_id.product_id, product)
        self.assertEqual(scan.packaging_id.barcode, "TEST-BOX")
        packaging = scan.packaging_id
        wizard.confirm()
        self.assertEqual(scan.packaging_id, packaging)
