# Copyright 2026 ACSONE SA/NV
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
from odoo.fields import Command

from odoo.addons.base.tests.common import BaseCommon


class TestPrintOperation(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.warehouse = cls.env.ref("stock.warehouse0")
        cls.product = cls.env["product.product"].create(
            {
                "name": "Test Product",
                "is_storable": True,
            }
        )
        cls.product_2 = cls.env["product.product"].create(
            {
                "name": "Test Product 2",
                "is_storable": True,
            }
        )

        cls.env["stock.quant"].with_context(inventory_mode=True).create(
            {
                "product_id": cls.product.id,
                "inventory_quantity": 10.0,
                "location_id": cls.warehouse.lot_stock_id.id,
            }
        )._apply_inventory()

        cls.env["stock.quant"].with_context(inventory_mode=True).create(
            {
                "product_id": cls.product_2.id,
                "inventory_quantity": 10.0,
                "location_id": cls.warehouse.lot_stock_id.id,
            }
        )._apply_inventory()

        cls.picking = cls.env["stock.picking"].create(
            {
                "picking_type_id": cls.warehouse.out_type_id.id,
                "move_ids": [
                    Command.create(
                        {
                            "name": "Test 1",
                            "product_id": cls.product.id,
                            "product_uom_qty": 5.0,
                            "location_id": cls.warehouse.lot_stock_id.id,
                            "location_dest_id": cls.env.ref(
                                "stock.stock_location_customers"
                            ).id,
                        }
                    ),
                    Command.create(
                        {
                            "name": "Test 2",
                            "product_id": cls.product_2.id,
                            "product_uom_qty": 4.0,
                            "location_id": cls.warehouse.lot_stock_id.id,
                            "location_dest_id": cls.env.ref(
                                "stock.stock_location_customers"
                            ).id,
                        }
                    ),
                ],
            }
        )

        cls.picking.action_confirm()

    def test_print_operation(self):
        self.move_product = self.picking.move_ids.filtered(
            lambda line: line.product_id == self.product
        )

        result = self.move_product.action_print_barcode()
        context = result.get("context")

        self.assertEqual(self.move_product.ids, context.get("default_move_ids"))
        self.assertEqual(
            self.move_product.product_id.ids, context.get("default_product_ids")
        )

    def test_print_operation_line(self):
        self.move_product = self.picking.move_line_ids.filtered(
            lambda line: line.product_id == self.product
        )

        result = self.move_product.action_print_line_barcode()
        context = result.get("context")

        self.assertEqual(self.move_product.ids, context.get("default_move_line_ids"))
        self.assertEqual(
            self.move_product.product_id.ids, context.get("default_product_ids")
        )

    def test_wizard(self):
        self.move_product = self.picking.move_line_ids.filtered(
            lambda line: line.product_id == self.product
        )

        result = self.move_product.action_print_line_barcode()
        context = result.get("context")
        wizard = self.env["product.label.layout"].with_context(**context).create({})
        self.assertEqual(wizard.move_line_ids, self.move_product)

        _xml_id, data = wizard._prepare_report_data()
        self.assertEqual(data.get("quantity_by_product"), {self.product.id: 5})
