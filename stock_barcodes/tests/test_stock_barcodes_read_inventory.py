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

    def test_apply_inventory_notifies_only_in_barcode_context(self):
        # Applying an inventory adjustment from outside the barcode wizard
        # (e.g. the product form "Update Quantity") must NOT push barcode users
        # back to the scan menu, so no "actions_barcode" notification is sent.
        quant = self.StockQuant.with_context(inventory_mode=True).create(
            {
                "product_id": self.product_wo_tracking.id,
                "location_id": self.location_1.id,
                "inventory_quantity": 5,
            }
        )
        with patch.object(type(quant), "send_bus_done") as mock_bus:
            quant.action_apply_inventory()
            scan_calls = [
                call
                for call in mock_bus.call_args_list
                if call.args and call.args[0] == "stock_barcodes_scan"
            ]
            self.assertFalse(scan_calls)

    def test_apply_inventory_notifies_in_barcode_context(self):
        # From the barcode wizard (barcode_apply_inventory flag) the adjustment
        # notifies the scan interface.
        quant = self.StockQuant.with_context(inventory_mode=True).create(
            {
                "product_id": self.product_wo_tracking.id,
                "location_id": self.location_2.id,
                "inventory_quantity": 7,
            }
        )
        with patch.object(type(quant), "send_bus_done") as mock_bus:
            quant.with_context(barcode_apply_inventory=True).action_apply_inventory()
            mock_bus.assert_any_call(
                "stock_barcodes_scan",
                {"type": "actions_barcode", "payload": {"apply_inventory": True}},
            )

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

    def test_inventory_preserves_other_owners(self):
        owner = self.test_partner_id
        other_owner = self.ResPartner.create({"name": "Other stock owner"})
        product = self.product_wo_tracking
        quants = self.StockQuant.with_context(inventory_mode=True)
        other_quant = quants.create(
            {
                "product_id": product.id,
                "location_id": self.location_1.id,
                "owner_id": other_owner.id,
                "inventory_quantity": 3,
            }
        )
        action = self.env.ref(
            "stock_barcodes.stock_barcodes_action_inventory"
        ).open_action()
        wiz = self.WizScanReadInventory.browse(action["res_id"])
        wiz.option_group_id.show_owner = True
        wiz.owner_id = owner
        if not wiz.display_read_quant:
            wiz.action_display_read_quant()
        self.assertEqual(other_quant.owner_id, other_owner)
        wiz.write(
            {
                "product_id": product.id,
                "location_id": self.location_1.id,
                "product_qty": 5,
                "manual_entry": True,
            }
        )
        self.assertTrue(wiz.action_confirm())
        own_quant = quants.search(
            [
                ("product_id", "=", product.id),
                ("location_id", "=", self.location_1.id),
                ("owner_id", "=", owner.id),
            ]
        )
        self.assertEqual(own_quant.inventory_quantity, 5)
        self.assertEqual(other_quant.owner_id, other_owner)
        self.assertEqual(other_quant.inventory_quantity, 3)
        other_quant.with_context(
            wiz_barcode_id=wiz.id
        ).action_barcode_inventory_quant_edit()
        self.assertEqual(wiz.owner_id, other_owner)
        wiz.product_qty = 4
        self.assertTrue(wiz.action_confirm())
        self.assertEqual(other_quant.inventory_quantity, 4)
        self.assertEqual(own_quant.inventory_quantity, 5)
