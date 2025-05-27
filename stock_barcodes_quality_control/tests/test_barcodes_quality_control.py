# Copyright 2025 Binhex <https://www.binhex.cloud>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from .test_barcodes_quality_control_common import TestQualityControlCommon


class TestQualityControl(TestQualityControlCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.action_qc_inspection = "quality_control_oca.action_qc_inspection"

    def test_action_validate_quality_control(self):
        action = self.wiz_scan.picking_id.action_validate_quality_control()
        self.assertEqual(action["type"], "ir.actions.act_window")
        self.assertEqual(action["xml_id"], self.action_qc_inspection)

    def test_wizard_action_validate_quality_control(self):
        action = self.wiz_quality_id.with_context(
            active_model=self.wiz_scan._name,
            active_id=self.wiz_scan.id,
        ).action_validate_quality_control()
        self.assertEqual(
            action["xml_id"], "stock_barcodes.action_stock_barcodes_action"
        )

        action = self.wiz_quality_id.with_context(
            go_validate_quality_control=True,
            active_model=self.wiz_scan._name,
            active_id=self.wiz_scan.id,
        ).action_validate_quality_control()
        self.assertEqual(action["xml_id"], self.action_qc_inspection)

    def test_compute_show_quantity_control(self):
        self.picking_id._compute_count_inspections()
        self.wiz_scan._compute_show_quantity_control()
        self.assertTrue(self.wiz_scan.show_quantity_control)
