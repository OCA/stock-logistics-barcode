# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from unittest.mock import patch

from odoo.tests.common import tagged

from .common import TestCommonStockBarcodes


@tagged("post_install", "-at_install")
class TestStockBarcodesReadInventory(TestCommonStockBarcodes):
    def test_action_display_read_quant(self):
        self.wiz_scan_read_inventory.action_display_read_quant()
        self.assertFalse(self.wiz_scan_read_inventory.display_read_quant)

        self.wiz_scan_read_inventory.display_read_quant = False
        self.wiz_scan_read_inventory.action_display_read_quant()
        self.assertTrue(self.wiz_scan_read_inventory.display_read_quant)

    def test_add_inventory_quant_done(self):
        self.wiz_scan_read_inventory.product_id = self.product_tracking.id
        self.wiz_scan_read_inventory.location_id = self.location_1.id
        self.wiz_scan_read_inventory.product_qty = 10
        self.wiz_scan_read_inventory.lot_id = self.lot_1.id
        self.wiz_scan_read_inventory.package_id = self.quant_package_1.id
        result = self.wiz_scan_read_inventory._add_inventory_quant()
        self.assertTrue(result)

        with (
            patch.object(type(self.wiz_scan_read_inventory), "_add_inventory_quant"),
            patch.object(
                type(self.wiz_scan_read_inventory), "action_clean_values"
            ) as mock_msg,
        ):
            self.wiz_scan_read_inventory.action_done()
            mock_msg.assert_called_once()

        with patch.object(
            type(self.wiz_scan_read_inventory), "_serial_tracking_message_fail"
        ) as mock_msg:
            self.wiz_scan_read_inventory.product_id = self.product_tracking_serial.id
            result = self.wiz_scan_read_inventory._add_inventory_quant()
            self.assertFalse(result)
            mock_msg.assert_called_once()

    def test_action_clean_values(self):
        with patch.object(
            type(self.wiz_scan_read_inventory), "send_bus_done"
        ) as mock_msg:
            self.wiz_scan_read_inventory.action_clean_values()
            self.assertEqual(self.wiz_scan_read_inventory.inventory_product_qty, 0)
            self.assertFalse(self.wiz_scan_read_inventory.package_id)
            self.assertFalse(self.wiz_scan_read_inventory.manual_entry)
            mock_msg.assert_called_once_with(
                "stock_barcodes_scan",
                {
                    "type": "stock_barcodes_edit_manual",
                    "payload": {"manual_entry": False},
                },
            )

    def test_onchange_product_lot_id(self):
        self.wiz_scan_read_inventory.product_id = self.product_tracking.id
        self.wiz_scan_read_inventory.onchange_product_id()
        self.assertFalse(self.wiz_scan_read_inventory.lot_id)

        self.wiz_scan_read_inventory.lot_id = self.lot_1.id
        self.wiz_scan_read_inventory._onchange_lot_id()
        self.assertFalse(self.wiz_scan_read_inventory.auto_lot)

    def test_accumulate_read_quantity(self):
        # With accumulate_read_quantity the scanned quantity is added to the
        # existing inventory quant instead of overwriting it.
        wiz = self.wiz_scan_read_inventory
        wiz.option_group_id.accumulate_read_quantity = True
        wiz.product_id = self.product_tracking
        wiz.location_id = self.location_1
        wiz.lot_id = self.lot_1
        wiz.product_qty = 3
        self.assertTrue(wiz._add_inventory_quant())
        wiz.product_qty = 2
        self.assertTrue(wiz._add_inventory_quant())
        quant = self.StockQuant.search(
            [
                ("product_id", "=", self.product_tracking.id),
                ("location_id", "=", self.location_1.id),
                ("lot_id", "=", self.lot_1.id),
            ],
            limit=1,
        )
        self.assertEqual(quant.inventory_quantity, 5.0)

    def test_overwrite_read_quantity(self):
        # Without accumulate_read_quantity the scanned quantity overwrites the
        # current inventory quantity.
        wiz = self.wiz_scan_read_inventory
        wiz.option_group_id.accumulate_read_quantity = False
        wiz.product_id = self.product_tracking
        wiz.location_id = self.location_1
        wiz.lot_id = self.lot_1
        wiz.product_qty = 3
        self.assertTrue(wiz._add_inventory_quant())
        wiz.product_qty = 2
        self.assertTrue(wiz._add_inventory_quant())
        quant = self.StockQuant.search(
            [
                ("product_id", "=", self.product_tracking.id),
                ("location_id", "=", self.location_1.id),
                ("lot_id", "=", self.lot_1.id),
            ],
            limit=1,
        )
        self.assertEqual(quant.inventory_quantity, 2.0)

    def test_compute_inventory_quant_ids_side_effect_free(self):
        # The compute must not emit bus notifications nor write any record.
        wiz = self.wiz_scan_read_inventory
        with patch.object(type(wiz), "send_bus_done") as mock_bus:
            wiz.invalidate_recordset(["inventory_quant_ids"])
            # Force the recomputation explicitly.
            wiz._compute_inventory_quant_ids()
            mock_bus.assert_not_called()

    def test_refresh_inventory_quants_sends_bus(self):
        wiz = self.wiz_scan_read_inventory
        with patch.object(type(wiz), "send_bus_done") as mock_bus:
            wiz._refresh_inventory_quants()
            mock_bus.assert_called_once_with(
                "stock_barcodes_form_update",
                {
                    "type": "count_apply_inventory",
                    "payload": {"count": wiz.count_inventory_quants},
                },
            )

    def test_refresh_inventory_quants_assigns_owner(self):
        # When show_owner is enabled and an owner is set, refreshing stamps the
        # owner on every displayed quant.
        wiz = self.wiz_scan_read_inventory
        wiz.option_group_id.show_owner = True
        wiz.invalidate_recordset(["show_owner"])
        wiz.owner_id = self.test_partner_id
        wiz.product_id = self.product_tracking
        wiz.location_id = self.location_1
        wiz.lot_id = self.lot_1
        wiz.product_qty = 3
        self.assertTrue(wiz._add_inventory_quant())
        # inventory_quant_ids does not depend on the quants, refresh the cache
        # so the newly created quant is taken into account.
        wiz.invalidate_recordset(["inventory_quant_ids"])
        with patch.object(type(wiz), "send_bus_done"):
            wiz._refresh_inventory_quants()
        self.assertTrue(wiz.inventory_quant_ids)
        self.assertTrue(
            all(q.owner_id == self.test_partner_id for q in wiz.inventory_quant_ids)
        )
