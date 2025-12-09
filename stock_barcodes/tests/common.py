# Copyright 2108-2019 Francois Poizat <francois.poizat@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import Command
from odoo.tests.common import TransactionCase

from odoo.addons.mail.tests.common import mail_new_test_user


class TestCommonStockBarcodes(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Active group_stock_packaging and group_production_lot for user
        group_stock_packaging = cls.env.ref("product.group_stock_packaging")
        group_production_lot = cls.env.ref("stock.group_production_lot")
        cls.env.user.groups_id = [
            (4, group_stock_packaging.id),
            (4, group_production_lot.id),
        ]
        # models
        cls.IrActionsWindow = cls.env["ir.actions.act_window"]
        cls.IrActions = cls.env["ir.actions.actions"]
        cls.Product = cls.env["product.product"]
        cls.ProductTemplate = cls.env["product.template"]
        cls.ProductPackaging = cls.env["product.packaging"]
        cls.WizScanReadPicking = cls.env["wiz.stock.barcodes.read.picking"]
        cls.WizScanReadInventory = cls.env["wiz.stock.barcodes.read.inventory"]
        cls.WizScanReadTodo = cls.env["wiz.stock.barcodes.read.todo"]
        cls.WizStockBarcodeRead = cls.env["wiz.stock.barcodes.read"]
        cls.WizCandidatePicking = cls.env["wiz.candidate.picking"]
        cls.StockProductionLot = cls.env["stock.lot"]
        cls.StockPicking = cls.env["stock.picking"]
        cls.StockQuant = cls.env["stock.quant"]
        cls.StockLocation = cls.env["stock.location"]
        cls.StockQuantpackage = cls.env["stock.quant.package"]
        cls.StockBarcodeAction = cls.env["stock.barcodes.action"]
        cls.StockMove = cls.env["stock.move"]
        cls.ActionReport = cls.env["ir.actions.report"]
        cls.StockPickingType = cls.env["stock.picking.type"]
        cls.ResUsers = cls.env["res.users"]
        cls.StockBarcodesOptionGroup = cls.env["stock.barcodes.option.group"]
        cls.StockMoveLine = cls.env["stock.move.line"]
        cls.ResPartner = cls.env["res.partner"]

        cls.company = cls.env.company

        # users
        cls.user_test = mail_new_test_user(
            cls.env,
            groups="stock.group_stock_user,stock.group_production_lot",
            login="test_user",
            name="Test user",
            signature="--\nTest user",
            company_id=cls.company.id,
        )

        cls.user_test_lot = mail_new_test_user(
            cls.env,
            groups="base.group_user,stock.group_tracking_lot",
            login="test_user_lot",
            name="Test user lot",
            signature="--\nTest user lot",
            company_id=cls.company.id,
        )

        cls.user_test_packing = mail_new_test_user(
            cls.env,
            groups="base.group_user,product.group_stock_packaging",
            login="test_user_packing",
            name="Test user packing",
            signature="--\nTest user packing",
            company_id=cls.company.id,
        )

        # Option groups for test
        cls.option_group = cls._create_barcode_option_group()
        cls.option_group1 = cls.StockBarcodesOptionGroup.create(
            {
                "name": "option group for tests 1",
                "option_ids": [
                    Command.create(
                        {
                            "step": 1,
                            "name": "Product forced",
                            "field_name": "product_id",
                            "forced": True,
                        }
                    ),
                ],
            }
        )
        cls.option_group2 = cls.StockBarcodesOptionGroup.create(
            {
                "name": "option group for tests 2",
                "option_ids": [
                    Command.create(
                        {
                            "step": 1,
                            "name": "Lot forced",
                            "field_name": "lot_id",
                            "forced": True,
                        }
                    ),
                ],
            }
        )
        cls.option_group3 = cls.StockBarcodesOptionGroup.create(
            {
                "name": "option group for tests 3",
                "option_ids": [
                    Command.create(
                        {
                            "step": 1,
                            "name": "Location forced",
                            "field_name": "location_id",
                            "forced": True,
                        }
                    ),
                ],
            }
        )
        cls.option_group4 = cls.StockBarcodesOptionGroup.create(
            {
                "name": "option group for tests 4",
                "option_ids": [
                    Command.create(
                        {
                            "step": 1,
                            "name": "Location forced",
                            "field_name": "location_dest_id",
                            "forced": True,
                        }
                    ),
                ],
            }
        )
        cls.option_group5 = cls.StockBarcodesOptionGroup.create(
            {
                "name": "option group for tests 5",
                "display_notification": True,
            }
        )
        cls.option_group6 = cls.StockBarcodesOptionGroup.create(
            {
                "name": "option group for tests 6",
                "barcode_guided_mode": "guided",
                "option_ids": [
                    Command.create(
                        {
                            "step": 1,
                            "name": "Location forced",
                            "field_name": "location_id",
                        }
                    ),
                ],
            }
        )
        cls.option_group7 = cls.StockBarcodesOptionGroup.create(
            {
                "name": "option group for tests 7",
                "barcode_guided_mode": "guided",
                "option_ids": [
                    Command.create(
                        {
                            "step": 1,
                            "name": "Package",
                            "field_name": "package_id",
                        }
                    ),
                ],
            }
        )

        cls.option_group8 = cls.StockBarcodesOptionGroup.create(
            {
                "name": "option group for tests 8",
                "barcode_guided_mode": "guided",
                "option_ids": [
                    Command.create(
                        {
                            "step": 1,
                            "name": "Product barcode guided",
                            "field_name": "product_id",
                            "forced": True,
                        }
                    ),
                ],
            }
        )
        cls.option_group9 = cls.StockBarcodesOptionGroup.create(
            {
                "name": "option group for tests 9",
                "use_location_dest_putaway": True,
                "source_pending_moves": False,
                "option_ids": [
                    Command.create(
                        {
                            "step": 1,
                            "name": "Product barcode guided",
                            "field_name": "location_dest_id",
                            "forced": True,
                        }
                    ),
                ],
            }
        )
        cls.option_group10 = cls.StockBarcodesOptionGroup.create(
            {
                "name": "option group for tests 9",
                "use_location_dest_putaway": True,
                "source_pending_moves": "move_line_ids",
                "allow_negative_quant": False,
            }
        )

        cls.stock_picking_type = cls.StockPickingType.create(
            {
                "name": "Test picking type",
                "sequence_code": "TEST",
                "new_picking_barcode_option_group_id": cls.option_group9.id,
            }
        )

        # warehouse and locations
        cls.warehouse = cls.env.ref("stock.warehouse0")
        cls.stock_location = cls.env.ref("stock.stock_location_stock")
        cls.stock_location_internal = cls.StockLocation.create(
            {
                "name": "Test location internal",
                "usage": "internal",
                "barcode": "8411322222111",
            }
        )
        cls.location_1 = cls.StockLocation.create(
            {
                "name": "Test location 1",
                "usage": "internal",
                "location_id": cls.stock_location.id,
                "barcode": "8411322222568",
            }
        )
        cls.location_2 = cls.StockLocation.create(
            {
                "name": "Test location 2",
                "usage": "internal",
                "location_id": cls.stock_location.id,
                "barcode": "8470001809032",
            }
        )

        # products
        cls.product_wo_tracking = cls.Product.create(
            {
                "name": "Product test wo lot tracking",
                "type": "product",
                "tracking": "none",
                "barcode": "8480000723208",
                "packaging_ids": [
                    Command.create(
                        {
                            "name": "Box 10 Units",
                            "qty": 10.0,
                            "barcode": "5099206074439",
                        }
                    )
                ],
            }
        )
        product_tracking_values = {
            "name": "Product test with lot tracking",
            "type": "product",
            "tracking": "lot",
            "barcode": "8433281006850",
            "packaging_ids": [
                Command.create(
                    {"name": "Box 5 Units", "qty": 5.0, "barcode": "5420008510489"}
                )
            ],
        }
        cls.product_tracking = cls.Product.create(product_tracking_values)
        product_tracking_values.update(
            {
                "tracking": "serial",
                "barcode": "84332810068950",
                "packaging_ids": [
                    Command.create(
                        {"name": "Box 15 Units", "qty": 5.0, "barcode": "5420008520489"}
                    )
                ],
            }
        )
        cls.product_tracking_serial = cls.Product.create(product_tracking_values)

        product_tracking_values.update(
            {
                "tracking": "serial",
                "barcode": "84332810068742",
                "packaging_ids": [
                    Command.create(
                        {
                            "name": "Box 15 Units",
                            "qty": 5.0,
                            "barcode": "84332810068722",
                        }
                    )
                ],
            }
        )
        cls.product_tracking_serial1 = cls.Product.create(product_tracking_values)

        cls.lot_1 = cls.StockProductionLot.create(
            {
                "name": "8411822222568",
                "product_id": cls.product_tracking.id,
                "company_id": cls.company.id,
            }
        )

        cls.lot_2 = cls.StockProductionLot.create(
            {
                "name": "8411822222999",
                "product_id": cls.product_tracking.id,
                "company_id": cls.company.id,
            }
        )
        cls.quant_package_1 = cls.StockQuantpackage.create({"name": "8411822222568"})
        quant_values = {
            "product_id": cls.product_tracking.id,
            "lot_id": cls.lot_1.id,
            "location_id": cls.stock_location.id,
            "quantity": 100.0,
            "package_id": cls.quant_package_1.id,
        }
        cls.quant_lot_1 = cls.StockQuant.create(quant_values)

        wiz_scan_values = {
            "option_group_id": cls.option_group.id,
            "step": 1,
        }
        cls.wiz_scan = cls.WizScanReadPicking.create(wiz_scan_values)
        wiz_scan_values.update({"option_group_id": cls.option_group1.id})
        cls.wiz_scan_option_forced = cls.WizScanReadPicking.create(wiz_scan_values)
        wiz_scan_values.update({"option_group_id": cls.option_group2.id})
        cls.wiz_scan_option_lot_forced = cls.WizScanReadPicking.create(wiz_scan_values)

        wiz_scan_values.update({"option_group_id": cls.option_group3.id})
        cls.wiz_scan_option_location_forced = cls.WizScanReadPicking.create(
            wiz_scan_values
        )

        wiz_scan_values.update({"option_group_id": cls.option_group4.id})
        cls.wiz_scan_option_location_dest_forced = cls.WizScanReadPicking.create(
            wiz_scan_values
        )

        wiz_scan_values.update({"option_group_id": cls.option_group5.id})
        cls.wiz_scan_option_display_notification = cls.WizScanReadPicking.create(
            wiz_scan_values
        )

        cls.wiz_scan_read_todo = cls.WizScanReadTodo.create(
            {
                "wiz_barcode_id": cls.wiz_scan.id,
                "line_ids": [
                    Command.create(
                        {
                            "product_id": cls.product_tracking.id,
                            "company_id": cls.company.id,
                            "location_id": cls.location_1.id,
                            "location_dest_id": cls.location_1.id,
                            "quantity_product_uom": 15,
                            "qty_picked": 10,
                        }
                    ),
                ],
            }
        )

        wiz_scan_values.update(
            {
                "option_group_id": cls.option_group6.id,
                "todo_line_id": cls.wiz_scan_read_todo.id,
            }
        )
        cls.wiz_scan_option_guided = cls.WizScanReadPicking.create(wiz_scan_values)

        cls.wiz_scan_read_inventory = cls.WizScanReadInventory.create(
            {"option_group_id": cls.option_group.id, "step": 1}
        )

        cls.wiz_scan_candidate_picking = cls.WizCandidatePicking.create(
            {"wiz_barcode_id": cls.wiz_scan.id}
        )

        # Barcode actions
        barcode_action_values = {
            "name": "Barcode action valid",
            "action_window_id": cls.env.ref("stock.stock_picking_type_action").id,
            "context": "{'search_default_barcode_options': 1}",
        }
        cls.barcode_action_valid = cls.StockBarcodeAction.create(barcode_action_values)

        cls.barcode_action_invalid = cls.StockBarcodeAction.create(
            {
                "name": "Barcode action valid",
            }
        )

        values_move = {
            "name": "Test move",
            "product_id": cls.product_tracking.id,
            "product_uom_qty": 1.0,
            "product_uom": cls.product_tracking.uom_id.id,
            "location_id": cls.stock_location.id,
            "location_dest_id": cls.stock_location.id,
            "state": "draft",
            "move_line_ids": [
                Command.create(
                    {
                        "product_id": cls.product_tracking.id,
                        "location_id": cls.stock_location.id,
                        "location_dest_id": cls.stock_location.id,
                        "company_id": cls.company.id,
                        "quantity": 0,
                        "quantity_product_uom": 10,
                    }
                )
            ],
        }

        cls.stock_move_test = cls.StockMove.create(values_move)
        values_move.update({"state": "assigned"})
        cls.stock_move_assigned = cls.StockMove.create(values_move)

        cls.picking = cls.StockPicking.create(
            {
                "location_id": cls.stock_location.id,
                "location_dest_id": cls.stock_location.id,
                "picking_type_id": cls.stock_picking_type.id,
            }
        )

        values_move.update(
            {
                "picking_id": cls.picking.id,
                "move_line_ids": values_move["move_line_ids"]
                + [
                    Command.create(
                        {
                            "picking_id": cls.picking.id,
                            "product_id": cls.product_tracking.id,
                            "location_id": cls.stock_location.id,
                            "location_dest_id": cls.stock_location.id,
                            "company_id": cls.company.id,
                            "quantity": 10,
                            "barcode_scan_state": "pending",
                            "quantity_product_uom": 10,
                        }
                    )
                ],
            }
        )
        cls.stock_move_assigned1 = cls.StockMove.create(values_move)
        line_values = {
            "picking_id": cls.picking.id,
            "product_id": cls.product_tracking.id,
            "location_id": cls.stock_location.id,
            "location_dest_id": cls.stock_location.id,
            "company_id": cls.company.id,
            "quantity": 20,
            "barcode_scan_state": "pending",
            "quantity_product_uom": 20,
        }
        cls.test_move_line = cls.StockMoveLine.create(line_values)
        line_values.update(
            {
                "quantity": 30,
                "quantity_product_uom": 30,
            }
        )
        cls.test_move_line1 = cls.StockMoveLine.create(line_values)
        line_values.update(
            {
                "quantity": 40,
                "quantity_product_uom": 40,
            }
        )
        cls.test_move_line2 = cls.StockMoveLine.create(line_values)
        cls.test_partner_id = cls.env["res.partner"].create(
            {
                "name": "Test partner",
            }
        )

    @classmethod
    def _create_barcode_option_group(cls, fill_fields_from_lot=False):
        return cls.env["stock.barcodes.option.group"].create(
            {
                "name": "option group for tests",
                "create_lot": True,
                "fill_fields_from_lot": fill_fields_from_lot,
                "option_ids": [
                    Command.create(
                        {
                            "step": 1,
                            "name": "Location",
                            "field_name": "location_id",
                            "to_scan": True,
                            "required": True,
                        }
                    ),
                    Command.create(
                        {
                            "step": 2,
                            "name": "Product",
                            "field_name": "product_id",
                            "to_scan": True,
                            "required": True,
                        }
                    ),
                    Command.create(
                        {
                            "step": 2,
                            "name": "Packaging",
                            "field_name": "packaging_id",
                            "to_scan": True,
                            "required": False,
                        }
                    ),
                    Command.create(
                        {
                            "step": 2,
                            "name": "Lot / Serial",
                            "field_name": "lot_id",
                            "to_scan": True,
                            "required": True,
                        }
                    ),
                ],
            }
        )

    def action_barcode_scanned(self, wizard, barcode):
        wizard._barcode_scanned = barcode
        wizard._on_barcode_scanned()
        # Method to call all methods outside of onchange environment for pickings read
        if wizard._name != "wiz.stock.barcodes.new.lot":
            wizard.dummy_on_barcode_scanned()
