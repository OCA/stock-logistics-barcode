# Copyright 2023 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo.tests import SavepointCase, tagged


@tagged("post_install", "-at_install")
class CommonProductBarcodeConstraintPerCompany(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.product_product_obj = cls.env["product.product"]
        cls.res_company_obj = cls.env["res.company"]
        cls.company_1 = cls.res_company_obj.create({"name": "Company 1"})
        cls.company_2 = cls.res_company_obj.create({"name": "Company 2"})

    @classmethod
    def _create_product(cls, name, company_id):
        return cls.product_product_obj.create(
            {
                "name": name,
                "company_id": company_id,
                "barcode": "978020137963",
            }
        )
