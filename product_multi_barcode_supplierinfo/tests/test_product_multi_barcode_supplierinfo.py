# © 2022 ForgeFlow S.L.
# Copyright 2026 NuoBiT Solutions - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.exceptions import ValidationError
from odoo.tests import Form, common


class TestProductMultiBarcodeSupplier(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product = cls.env["product.product"].create({"name": "Test product"})
        cls.partner = cls.env["res.partner"].create({"name": "Test Partner"})
        cls.barcode = "123456789"

    def new_supplier(self):
        form = Form(
            self.env["product.supplierinfo"].with_context(visible_product_tmpl_id=False)
        )
        form.partner_id = self.partner
        form.product_tmpl_id = self.product.product_tmpl_id
        return form

    def _create_multi_variant_template(self):
        attribute = self.env["product.attribute"].create({"name": "Test Size"})
        values = self.env["product.attribute.value"].create(
            [
                {"name": "S", "attribute_id": attribute.id},
                {"name": "M", "attribute_id": attribute.id},
            ]
        )
        return self.env["product.template"].create(
            {
                "name": "Test product with variants",
                "attribute_line_ids": [
                    (
                        0,
                        0,
                        {
                            "attribute_id": attribute.id,
                            "value_ids": [(6, 0, values.ids)],
                        },
                    )
                ],
            }
        )

    def test01_set_barcode_from_supplier(self):
        form = self.new_supplier()
        form.barcode = self.barcode
        form.save()
        self.assertEqual(self.product.barcode_ids.name, self.barcode)

    def test02_delete_barcode_from_supplier(self):
        form = self.new_supplier()
        form.barcode = self.barcode
        supplierinfo = form.save()
        supplierinfo.unlink()
        self.assertTrue(not self.product.barcode_ids)

    def test03_rename_barcode_from_supplier(self):
        form = self.new_supplier()
        form.barcode = self.barcode
        supplierinfo = form.save()
        barcode = self.product.barcode_ids
        supplierinfo.barcode = "987654321"
        self.assertEqual(barcode.name, "987654321")
        self.assertEqual(self.product.barcode_ids, barcode)

    def test04_link_existing_barcode(self):
        existing = self.env["product.barcode"].create(
            {
                "name": self.barcode,
                "product_tmpl_id": self.product.product_tmpl_id.id,
            }
        )
        form = self.new_supplier()
        form.barcode = self.barcode
        supplierinfo = form.save()
        self.assertEqual(supplierinfo.barcode_id, existing)
        self.assertEqual(existing.supplier_id, self.partner)
        self.assertEqual(len(self.product.barcode_ids), 1)

    def test05_variant_required_for_barcode(self):
        template = self._create_multi_variant_template()
        with self.assertRaises(ValidationError):
            self.env["product.supplierinfo"].create(
                {
                    "partner_id": self.partner.id,
                    "product_tmpl_id": template.id,
                    "barcode": "111111111",
                }
            )

    def test06_variant_barcode_from_supplier(self):
        template = self._create_multi_variant_template()
        variant = template.product_variant_ids[1]
        supplierinfo = self.env["product.supplierinfo"].create(
            {
                "partner_id": self.partner.id,
                "product_tmpl_id": template.id,
                "product_id": variant.id,
                "barcode": "222222222",
            }
        )
        self.assertEqual(supplierinfo.barcode_id.product_id, variant)
        self.assertEqual(variant.barcode_ids.name, "222222222")
