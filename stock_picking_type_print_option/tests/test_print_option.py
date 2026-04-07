# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from markupsafe import Markup

from odoo.addons.base.tests.common import BaseCommon


class TestPrintOption(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.label_wizard = cls.env["product.label.layout"]
        cls.warehouse = cls.env.ref("stock.warehouse0")
        cls.type_int = cls.warehouse.int_type_id
        cls.product = cls.env["product.product"].create(
            {
                "name": "Product Test",
                "is_storable": True,
            }
        )
        cls.pricelist = cls.env["product.pricelist"].create({"name": "Test Pricelist"})

        cls.type_int.print_label_option_print_format = "zpl"
        cls.type_int.print_label_option_pricelist_id = cls.pricelist.id
        cls.type_int.print_label_option_move_quantity = "move"
        cls.type_int.print_label_option_extra_html = "Test HTML"

        cls._create_picking_and_quantity()

    @classmethod
    def _create_picking_and_quantity(cls):
        cls.env["stock.quant"].create(
            {
                "product_id": cls.product.id,
                "inventory_quantity": 10.0,
                "location_id": cls.warehouse.lot_stock_id.id,
            }
        )._apply_inventory()
        cls.move = cls.env["stock.move"].create(
            {
                "name": cls.product.name,
                "product_id": cls.product.id,
                "product_uom_qty": 5.0,
                "product_uom": cls.product.uom_id.id,
                "picking_type_id": cls.warehouse.int_type_id.id,
                "location_id": cls.warehouse.lot_stock_id.id,
                "location_dest_id": cls.warehouse.wh_qc_stock_loc_id.id,
            }
        )
        cls.move._action_confirm()

    def test_print_options(self):
        action = self.move.picking_id.action_open_label_type()
        self.assertEqual(
            action["context"].get("default_print_format"),
            "zpl",
        )
        self.assertEqual(
            action["context"].get("default_pricelist_id"),
            self.pricelist.id,
        )
        self.assertEqual(
            action["context"].get("default_move_quantity"),
            "move",
        )
        self.assertEqual(
            action["context"].get("default_extra_html"),
            Markup("<p>Test HTML</p>"),
        )
