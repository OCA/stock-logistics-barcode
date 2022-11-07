# © 2022 ForgeFlow S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests import Form, common


class TestProductMultiBarcodeSupplier(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestProductMultiBarcodeSupplier, cls).setUpClass()
        cls.product = cls.env["product.product"].create({"name": "Test product"})
        cls.partner = cls.env["res.partner"].create({"name": "Test Partner"})
        cls.barcode = "123456789"

    def new_supplier(self):
        form = Form(self.env["product.supplierinfo"])
        form.name = self.partner
        form.product_tmpl_id = self.product.product_tmpl_id
        return form

    def test01_set_barcode_from_supplier(self):
        form = self.new_supplier()
        form.barcode = self.barcode
        form.save()
        self.assertEqual(self.product.barcode_ids.name, self.barcode)

    def test02_delete_barcode_from_supplier(self):
        form = self.new_supplier()
        form.barcode = self.barcode
        form.save()
        supplierinfo = self.env["product.supplierinfo"].browse(form._values["id"])
        supplierinfo.unlink()
        self.assertTrue(not self.product.barcode_ids)
