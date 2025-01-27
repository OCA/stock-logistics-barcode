# Copyright 2108-2019 Sergio Teruel <sergio.teruel@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import re

from odoo.exceptions import ValidationError
from odoo.tests.common import tagged

from odoo.addons.stock_barcodes.models.stock_barcodes_action import FIELDS_NAME, REGEX

from .common import TestCommonStockBarcodes


@tagged("post_install", "-at_install")
class TestStockBarcodes(TestCommonStockBarcodes):
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
        self.assertEqual(self.barcode_action_valid._count_elements(), 6)
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
