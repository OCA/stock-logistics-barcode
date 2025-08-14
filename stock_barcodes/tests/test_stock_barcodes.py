# Copyright 2108-2019 Sergio Teruel <sergio.teruel@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import base64
import re
from unittest.mock import call, patch

from odoo import _
from odoo.exceptions import ValidationError
from odoo.tests.common import tagged
from odoo.tools.safe_eval import safe_eval

from odoo.addons.stock_barcodes.models.stock_barcodes_action import FIELDS_NAME, REGEX

from .common import TestCommonStockBarcodes


@tagged("post_install", "-at_install")
class TestStockBarcodes(TestCommonStockBarcodes):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.send_bus_done_calls = []

    def fake_send_bus_done(self, channel, notif_type, data):
        self.send_bus_done_calls.append((channel, notif_type, data))

    def test_wizard_scan_location(self):
        self.action_barcode_scanned(self.wiz_scan, "8411322222568")
        self.assertEqual(self.wiz_scan.location_id, self.location_1)

    def test_wizard_scan_product(self):
        self.wiz_scan.location_id = self.location_1
        self.wiz_scan.action_show_step()
        self.action_barcode_scanned(self.wiz_scan, "8480000723208")
        self.assertEqual(self.wiz_scan.product_id, self.product_wo_tracking)
        self.assertEqual(self.wiz_scan.product_qty, 1.0)

    def test_wizard_scan_product_manual_entry(self):
        # Test manual entry
        self.wiz_scan.manual_entry = True
        self.wiz_scan.location_id = self.location_1
        self.wiz_scan.action_show_step()
        self.action_barcode_scanned(self.wiz_scan, "8480000723208")
        self.assertEqual(self.wiz_scan.product_qty, 0.0)
        self.wiz_scan.product_qty = 50.0

    def test_wizard_scan_package(self):
        self.wiz_scan.location_id = self.location_1
        self.wiz_scan.action_show_step()
        self.action_barcode_scanned(self.wiz_scan, "5420008510489")
        self.assertEqual(self.wiz_scan.product_id, self.product_tracking)
        self.assertEqual(self.wiz_scan.product_qty, 5.0)
        self.assertEqual(
            self.wiz_scan.packaging_id, self.product_tracking.packaging_ids
        )

        # Manual entry
        self.wiz_scan.manual_entry = True
        self.wiz_scan.action_clean_values()
        self.action_barcode_scanned(self.wiz_scan, "5420008510489")
        self.assertEqual(self.wiz_scan.packaging_qty, 1.0)
        self.wiz_scan.packaging_qty = 3.0
        self.wiz_scan.onchange_packaging_qty()
        self.assertEqual(self.wiz_scan.product_qty, 15.0)
        self.wiz_scan.manual_entry = False

    def test_wizard_scan_lot(self):
        self.wiz_scan.location_id = self.location_1.id
        self.wiz_scan.action_show_step()
        self.action_barcode_scanned(self.wiz_scan, "8411822222568")
        # Lot found for one product, so product_id is filled
        self.assertTrue(self.wiz_scan.product_id)
        self.action_barcode_scanned(self.wiz_scan, "8433281006850")
        self.action_barcode_scanned(self.wiz_scan, "8411822222568")
        self.assertEqual(self.wiz_scan.lot_id, self.lot_1)
        # After scan other product, set wizard lot to False
        self.action_barcode_scanned(self.wiz_scan, "8480000723208")
        self.assertFalse(self.wiz_scan.lot_id)

    def test_wizard_scan_not_found(self):
        self.action_barcode_scanned(self.wiz_scan, "84118xxx22568")
        self.assertEqual(
            self.wiz_scan.message,
            "84118xxx22568 (Barcode not found with this screen values)",
        )

    def test_wiz_clean_lot(self):
        self.wiz_scan.location_id = self.location_1.id
        self.wiz_scan.action_show_step()
        self.action_barcode_scanned(self.wiz_scan, "8433281006850")
        self.action_barcode_scanned(self.wiz_scan, "8411822222568")
        self.wiz_scan.action_clean_lot()
        self.assertFalse(self.wiz_scan.lot_id)

    def test_barcode_action(self):
        self.assertTrue(self.barcode_action_valid.action_window_id)
        self.assertEqual(bool(self.barcode_action_invalid.action_window_id), False)

    def test_action_back(self):
        result = self.wiz_scan.action_back()
        self.assertIn("name", result)
        self.assertIn("type", result)
        self.assertIn("res_model", result)
        self.assertEqual(result["type"], "ir.actions.act_window")

    def test_barcode_context_action(self):
        context = self.barcode_action_valid.context
        self.assertTrue(bool(re.match(REGEX.get("context", ""), context)))
        self.assertGreater(len(context), 0)
        context = context.strip("{}").split(",")
        field_values = context[0].split(":")
        self.assertGreater(len(field_values), 1)
        field_name = field_values[0].split("search_default_")
        self.assertGreater(len(field_name), 1)
        field_value_format = field_values[1].replace("'", "").strip()
        self.assertTrue(field_value_format.isdigit())
        self.assertEqual(field_values[0].strip("'"), "search_default_barcode_options")
        self.assertTrue(len(field_values[0].split("search_default_")), 2)
        self.assertEqual(self.barcode_action_invalid._count_elements(), 0)
        self.barcode_action_invalid.context = False
        with self.assertRaises(TypeError):
            self.barcode_action_invalid._compute_count_elements()
        self.barcode_action_invalid.context = "{}"
        self.assertFalse("search_default_" in self.barcode_action_invalid.context)

        self.assertEqual(self.barcode_action_invalid._count_elements(), 0)
        self.barcode_action_valid.context = "{'search_default_code': 1}"
        # self.assertEqual(self.barcode_action_valid._count_elements(), 5)
        field_value_name = (
            self.barcode_action_valid.context.strip("{}").split(",")[0].split(":")
        )
        field_name = field_value_name[0].split("search_default_")[1].strip("'")
        self.assertTrue("search_default_" in self.barcode_action_valid.context)
        self.assertFalse(
            hasattr(
                self.barcode_action_valid.action_window_id.res_model,
                FIELDS_NAME.get(field_name, field_name),
            )
        )
        field_values = field_value_name[1].strip()
        self.assertTrue(field_values.isdigit())

        with self.assertRaises(IndexError):
            self.barcode_action_invalid.context = "{'search_default_'}"
            self.assertEqual(self.barcode_action_invalid._count_elements(), 0)
        with self.assertRaises(ValidationError):
            self.StockBarcodeAction.create(
                {
                    "name": "Barcode action invalid with space",
                    "context": "{'search_default_code': 'incoming'}  ",
                }
            )

    def test_duplicate_barcode(self):
        self.StockBarcodeAction.create(
            {
                "name": "Action 1",
                "barcode": "DUPLICATE001",
            }
        )
        with self.assertRaises(ValidationError):
            self.StockBarcodeAction.create(
                {
                    "name": "Action 2",
                    "barcode": "DUPLICATE001",
                }
            )

    def test_valid_invalid_barcode(self):
        action = self.StockBarcodeAction.create(
            {
                "name": "Valid Barcode Test",
                "barcode": "1597536458",
            }
        )
        self.assertEqual(action.barcode, "1597536458")
        with self.assertRaises(ValidationError):
            self.StockBarcodeAction.create(
                {
                    "name": "Invalid Barcode Test",
                    "barcode": "1597 536458",
                }
            )

    def test_generate_barcode_returns_base64_image(self):
        action = self.StockBarcodeAction.create(
            {
                "name": "Barcode Image Test",
                "barcode": "1597536458",
            }
        )
        image_base64 = action._generate_barcode()
        self.assertIsInstance(image_base64, bytes, "The result must be a bytes object")
        decoded = base64.b64decode(image_base64)
        self.assertTrue(len(decoded) > 0, "The generated image cannot be empty")
        self.assertTrue(
            decoded.startswith(b"\x89PNG") or decoded.startswith(b"\xff\xd8"),
            "The image does not appear to be valid (neither PNG nor JPEG)",
        )

        action_without_barcode = self.StockBarcodeAction.create(
            {
                "name": "Barcode Image Test",
                "barcode": False,
            }
        )
        action_without_barcode._compute_barcode_image()
        self.assertFalse(
            action_without_barcode.barcode_image,
            "If the barcode is not configured, the image is not generated.",
        )

    def test_open_action_basic(self):
        action = self.barcode_action_valid.open_action()
        self.assertIn("context", action)
        merged_ctx = action["context"]
        self.assertEqual(merged_ctx.get("search_default_barcode_options"), 1)

    def test_open_inventory_action_called(self):
        action_inventory_id = "stock_barcodes.action_stock_barcodes_read_inventory"
        record = self.StockBarcodeAction.create(
            {
                "name": "Test Action",
                "action_window_id": self.env.ref(action_inventory_id).id,
                "context": "{'inventory_mode': True}",
            }
        )
        patch_return_value = {
            "name": "Inventory",
            "id": action_inventory_id,
            "type": "ir.actions.act_window",
        }
        with patch.object(
            type(record), "open_inventory_action", return_value=patch_return_value
        ) as mock_method:
            result = record.open_action()
            mock_method.assert_called_once()
            self.assertEqual(result["id"], action_inventory_id)
            self.assertEqual(result["name"], "Inventory")
            self.assertEqual(result["type"], "ir.actions.act_window")
            action_context = safe_eval(record.action_window_id.context)
            self.assertTrue(
                action_context.get("inventory_mode", False),
                "The context must have at least the value 'inventory_mode': True",
            )

    def test_print_barcodes(self):
        record = self.StockBarcodeAction.create({"name": "Test Barcode Action"})
        with patch.object(
            type(self.ActionReport), "report_action"
        ) as mock_report_action:
            mock_report_action.return_value = {
                "type": "ir.actions.report",
                "report_name": "barcode_report",
            }
            report_action = record.print_barcodes()
            mock_report_action.assert_called_once()
            self.assertEqual(
                report_action,
                {"type": "ir.actions.report", "report_name": "barcode_report"},
            )

    def test_display_assign_serial(self):
        self.wiz_scan_read_inventory.write({"product_id": self.product_tracking_serial})
        self.assertTrue(self.wiz_scan_read_inventory.display_assign_serial)
        self.wiz_scan_read_inventory.write({"product_id": self.product_wo_tracking})
        self.assertFalse(self.wiz_scan_read_inventory.display_assign_serial)

    def test_create_lot(self):
        self.wiz_scan._compute_create_lot()
        self.assertTrue(self.wiz_scan.create_lot)

        self.wiz_scan.option_group_id.create_lot = False
        self.wiz_scan._compute_create_lot()
        self.assertFalse(self.wiz_scan.create_lot)

    def test_set_messagge_info(self):
        self.wiz_scan.barcode = "ABC123"
        message_type = "info"
        message = "MESSAGE INFO"
        self.wiz_scan._set_messagge_info(message_type=message_type, message=message)
        self.assertFalse(self.wiz_scan.manual_entry)
        expected_msg = "{} ({})".format("ABC123", message)
        self.assertEqual(self.wiz_scan.message, expected_msg)
        self.assertEqual(self.wiz_scan.message_type, message_type)
        self.assertFalse(getattr(self.wiz_scan, "manual_entry", False))
        self.assertEqual(len(self.send_bus_done_calls), 0)

        self.wiz_scan.barcode = False
        message = "NOT FOUND"
        message_type = "not_found"
        bus_data = {
            "message": message,
            "sticky": True,
            "message_type": "danger",
        }
        self.wiz_scan.manual_entry = False
        self.wiz_scan._set_messagge_info(message_type, message)
        self.fake_send_bus_done(
            "stock_barcodes_scan", "actions_barcode_notification", bus_data
        )

        self.assertTrue(self.wiz_scan.manual_entry)
        self.assertEqual(len(self.send_bus_done_calls), 1)
        channel, notif_type, data = self.send_bus_done_calls[0]
        self.assertEqual(channel, "stock_barcodes_scan")
        self.assertEqual(notif_type, "actions_barcode_notification")
        self.assertEqual(data["message"], message)
        self.assertTrue(data.get("sticky", False))
        self.assertEqual(data["message_type"], "danger")

    def test_process_barcode_location_dest_id(self):
        self.wiz_scan.barcode = "8411322222568"
        location_dest = self.wiz_scan.process_barcode_location_dest_id()
        self.assertTrue(location_dest)

        self.wiz_scan.barcode = "8411322233568"
        location_dest = self.wiz_scan.process_barcode_location_dest_id()
        self.assertFalse(location_dest)

    def test_process_barcode_product_id(self):
        self.wiz_scan.barcode = "8433281007050"
        barcode_product = self.wiz_scan.process_barcode_product_id()
        self.assertFalse(barcode_product)

        with patch.object(type(self.Product), "search_count", return_value=2):
            barcode_product = self.wiz_scan.process_barcode_product_id()
            self.assertFalse(barcode_product)

        with patch.object(type(self.Product), "create"):
            barcode_product = self.wiz_scan.process_barcode_product_id()
            self.assertFalse(barcode_product)

        product_data = {
            "name": "Product service",
            "type": "service",
            "list_price": 100.0,
            "barcode": "1234896568",
        }
        fake_product = self.ProductTemplate.browse(42)
        with patch.object(
            type(self.ProductTemplate), "create", return_value=fake_product
        ) as mock_create:
            product_id = self.ProductTemplate.create(product_data)
            mock_create.assert_called_once_with(product_data)
            self.wiz_scan.barcode = "1234896568"
            self.wiz_scan.product_id = product_id.id
            barcode_product = self.wiz_scan.process_barcode_product_id()
            self.assertFalse(barcode_product)

    def test_compute_action_ids(self):
        self.WizStockBarcodeRead._compute_action_ids()
        action_ids = self.wiz_scan.action_ids.ids
        self.assertIn(self.barcode_action_valid.id, action_ids)
        self.assertGreaterEqual(len(action_ids), 1)
        self.wiz_scan.onchange_visible_force_done()
        self.assertFalse(self.wiz_scan.visible_force_done)

    def test_process_barcode_lot_id(self):
        lot_id = self.wiz_scan.process_barcode_lot_id()
        self.assertFalse(lot_id)

        self.wiz_scan.barcode = "8411822222568"
        lot_id = self.wiz_scan.with_user(self.user_test).process_barcode_lot_id()
        self.assertTrue(lot_id)
        self.assertEqual(self.wiz_scan.product_id, self.lot_1.product_id)
        self.wiz_scan.option_group_id.fill_fields_from_lot = True

    def test_process_barcode_package_id(self):
        package = self.wiz_scan.process_barcode_package_id()
        self.assertFalse(package)
        wiz_scan_user = self.wiz_scan.with_user(self.user_test_lot)
        self.wiz_scan.barcode = "8411822222568"
        self.wiz_scan.location_id = self.stock_location.id
        result = wiz_scan_user.process_barcode_package_id()
        self.assertTrue(result)

        self.wiz_scan.location_id = self.stock_location_internal.id
        result = wiz_scan_user.process_barcode_package_id()
        self.assertTrue(result)

        self.wiz_scan.barcode = "8411822222599"
        self.wiz_scan.location_id = self.stock_location_internal.id
        result = wiz_scan_user.process_barcode_package_id()
        self.assertFalse(result)

        self.wiz_scan.owner_id = self.user_test.partner_id.id
        result = wiz_scan_user.process_barcode_package_id()
        self.assertFalse(result)

    def test_process_barcode_result_package_id(self):
        package = self.wiz_scan.process_barcode_result_package_id()
        self.assertFalse(package)

        wiz_scan_user = self.wiz_scan.with_user(self.user_test_lot)
        self.wiz_scan.barcode = "84118222225681"
        result = wiz_scan_user.process_barcode_result_package_id()
        self.assertFalse(result)

        self.wiz_scan.barcode = "8411822222568"
        result = wiz_scan_user.process_barcode_result_package_id()
        self.assertTrue(result)

    def test_process_barcode_packaging_id(self):
        packing = self.wiz_scan.process_barcode_packaging_id()
        self.assertFalse(packing)

        packing_values = {
            "name": "Test product packing",
            "product_uom_id": self.env.ref("uom.product_uom_unit").id,
            "product_id": self.env.ref("product.product_product_4").id,
            "barcode": "8411822222568",
        }
        self.ProductPackaging.create(packing_values)

        wiz_scan_user = self.wiz_scan.with_user(self.user_test_packing)
        self.wiz_scan.barcode = "8411822222568"
        result = wiz_scan_user.process_barcode_packaging_id()
        self.assertTrue(result)

    def test_scanned_location(self):
        with patch.object(
            type(self.wiz_scan),
            "_barcode_domain",
            return_value=[("barcode", "=", "8411322222111")],
        ), patch.object(type(self.wiz_scan), "_set_messagge_info") as mock_msg:
            result = self.wiz_scan._scanned_location("8411322222111")
            self.assertTrue(result)
            self.assertEqual(self.wiz_scan.location_id, self.stock_location_internal)
            mock_msg.assert_called_once_with("info", _("Waiting product"))

        result = self.wiz_scan._scanned_location("8411322222111111")
        self.assertFalse(result)

    def test_check_location_contidion(self):
        with patch.object(
            type(self.wiz_scan), "check_location_contidion", return_value=False
        ):
            result = self.wiz_scan.check_location_contidion()
            self.assertFalse(result)
            self.assertEqual(bool(self.wiz_scan.product_id), False)

    def test_check_done_conditions(self):
        with patch.object(
            type(self.wiz_scan), "check_location_contidion", return_value=False
        ) as mock_msg:
            self.wiz_scan.product_id = self.product_tracking.id
            result = self.wiz_scan.check_done_conditions()
            self.assertFalse(result)
            mock_msg.assert_called_once()

        with patch.object(
            type(self.wiz_scan), "check_lot_contidion", return_value=False
        ):
            result = self.wiz_scan.check_done_conditions()
            self.assertFalse(result)

        with patch.object(
            type(self.wiz_scan), "check_location_contidion", return_value=True
        ), patch.object(
            type(self.wiz_scan), "check_lot_contidion", return_value=True
        ), patch.object(type(self.wiz_scan), "_set_messagge_info") as mock_msg:
            self.wiz_scan.product_qty = 0
            self.wiz_scan.product_id = self.product_tracking.id
            result = self.wiz_scan.check_done_conditions()
            self.assertFalse(result)
            mock_msg.assert_called_once_with("info", _("Waiting quantities"))

    def test_check_guided_values(self):
        result = self.wiz_scan_option_forced._check_guided_values()
        self.assertTrue(result)
        with patch.object(type(self.wiz_scan), "_set_messagge_info") as mock_msg:
            # 1 condition
            self.wiz_scan_option_forced.product_id = self.product_tracking.id
            self.wiz_scan_option_forced.guided_product_id = (
                self.product_tracking_serial.id
            )
            result = self.wiz_scan_option_forced._check_guided_values()
            self.assertFalse(result)

            # 2 condition
            self.assertEqual(self.wiz_scan_option_forced.product_qty, 0)
            self.wiz_scan_option_lot_forced.product_id = self.product_tracking.id
            self.wiz_scan_option_lot_forced.lot_id = self.lot_1.id
            self.wiz_scan_option_lot_forced.guided_lot_id = self.lot_2.id
            result = self.wiz_scan_option_lot_forced._check_guided_values()
            self.assertFalse(result)

            # 3 condition
            self.wiz_scan_option_location_forced.location_id = self.location_1.id
            self.wiz_scan_option_location_forced.guided_location_id = self.location_2.id
            result = self.wiz_scan_option_location_forced._check_guided_values()
            self.assertFalse(result)

            # 4 condition
            self.wiz_scan_option_location_dest_forced.location_dest_id = (
                self.location_1.id
            )
            self.wiz_scan_option_location_dest_forced.guided_location_dest_id = (
                self.location_2.id
            )
            result = self.wiz_scan_option_location_dest_forced._check_guided_values()
            self.assertFalse(result)

            mock_msg.assert_has_calls(
                [
                    call("more_match", _("Wrong product")),  # 1 condition
                    call("more_match", _("Wrong lot")),  # 2 condition
                    call("more_match", _("Wrong location")),  # 3 condition
                    call("more_match", _("Wrong location dest")),  # 4 condition
                ]
            )

    def test_action_done(self):
        with patch.object(type(self.wiz_scan), "_set_messagge_info") as mock_msg:
            self.wiz_scan.product_qty = 10000000
            result = self.wiz_scan.action_done()
            self.assertFalse(result)
            mock_msg.assert_called_once_with("more_match", _("The quantity is huge"))

    def test_action_lot_scaned_post(self):
        self.wiz_scan.action_lot_scaned_post(self.lot_1.name)
        self.assertEqual(self.wiz_scan.lot_name, self.lot_1.name)
        self.assertFalse(self.wiz_scan.lot_id)

        self.wiz_scan.product_id = self.product_tracking.id
        result = self.wiz_scan._create_new_lot()
        self.assertEqual(result.id, self.lot_1.id)

        mock_values = {
            "name": self.lot_1.name,
            "product_id": self.product_tracking_serial1.id,
            "company_id": self.env.company.id,
        }
        with patch.object(
            type(self.wiz_scan), "_prepare_lot_vals", return_value=mock_values
        ) as mock_msg:
            self.wiz_scan.product_id = self.product_tracking_serial.id
            result = self.wiz_scan._create_new_lot()
            self.assertEqual(result.name, self.lot_1.name)
            mock_msg.assert_called_once()

        self.wiz_scan.lot_name = False
        self.wiz_scan.action_lot_scaned_post(self.lot_1.id)
        self.assertEqual(self.wiz_scan.lot_id.id, self.lot_1.id)

    def test_action_clean_product_package(self):
        with patch.object(type(self.wiz_scan), "action_show_step") as mock_msg:
            self.wiz_scan.action_show_step()
            self.assertFalse(self.wiz_scan.product_id)
            mock_msg.assert_called_once()

        with patch.object(type(self.wiz_scan), "action_show_step") as mock_msg:
            self.wiz_scan.action_clean_package()
            self.assertFalse(self.wiz_scan.package_id)
            self.assertFalse(self.wiz_scan.result_package_id)
            mock_msg.assert_called_once()

        self.wiz_scan.reset_qty()
        self.assertEqual(self.wiz_scan.product_qty, 0)
        self.assertEqual(self.wiz_scan.packaging_qty, 0)

        result = self.wiz_scan.open_actions()
        self.assertTrue(self.wiz_scan.display_menu)
        self.assertIsInstance(result, dict)
        self.assertEqual(result["type"], "ir.actions.client")
        self.assertEqual(
            result["xml_id"], "stock_barcodes.action_stock_barcodes_action_client"
        )

        self.wiz_scan.action_force_done()
        self.assertFalse(self.wiz_scan.visible_force_done)

        self.wiz_scan.manual_entry = True
        self.wiz_scan.package_id = self.quant_package_1.id
        self.wiz_scan.onchange_package_id()
        self.assertEqual(self.wiz_scan.barcode, self.quant_package_1.name)

    def test_action_add_scan_manual(self):
        with patch.object(type(self.wiz_scan), "send_bus_done") as mock_msg:
            self.wiz_scan.action_add_scan_manual()
            self.assertTrue(self.wiz_scan.manual_entry)
            mock_msg.assert_called_once_with(
                "stock_barcodes_scan",
                "stock_barcodes_edit_manual",
                {"manual_entry": True},
            )

    def test_action_clean_message(self):
        with patch.object(type(self.wiz_scan), "check_option_required") as mock_msg:
            self.wiz_scan.action_clean_message()
            self.assertFalse(self.wiz_scan.message)
            mock_msg.assert_called_once()

        self.wiz_scan.keep_result_package = True
        self.wiz_scan.action_keep_result_package()
        self.assertFalse(self.wiz_scan.keep_result_package)

        self.wiz_scan.keep_result_package = False
        self.wiz_scan.action_keep_result_package()
        self.assertTrue(self.wiz_scan.keep_result_package)

    def test_display_notification(self):
        message_title = "Title test"
        message = "Message test"
        message_notification = {
            "title": message_title,
            "message": message,
            "type": "warning",
            "sticky": True,
            "res_model": self.wiz_scan_option_display_notification._name,
            "res_id": self.wiz_scan_option_display_notification.ids[0],
        }
        with patch.object(type(self.wiz_scan), "send_bus_done") as mock_msg:
            self.wiz_scan_option_display_notification.display_notification(
                title=message_title, message=message
            )
            mock_msg.assert_called_once_with(
                f"stock_barcodes-{self.wiz_scan_option_display_notification.ids[0]}",
                f"stock_barcodes_notify-{self.wiz_scan_option_display_notification.ids[0]}",
                message_notification,
            )
