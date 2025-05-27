# Copyright 2025 Binhex <https://www.binhex.cloud>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.quality_control_oca.tests.test_quality_control import (
    TestQualityControlOcaBase,
)
from odoo.addons.stock_barcodes.tests.common import TestCommonStockBarcodes


class TestQualityControlCommon(TestQualityControlOcaBase, TestCommonStockBarcodes):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.WizardQualityControl = cls.env["quality.control.validate.wizard"]
        cls.StockPicking = cls.env["stock.picking"]
        cls.picking_type_in = cls.env.ref("stock.picking_type_in")
        cls.picking_id = cls.StockPicking.create(
            {
                "picking_type_id": cls.picking_type_in.id,
                "location_id": cls.location_1.id,
                "location_dest_id": cls.location_2.id,
                "move_ids": [
                    (
                        0,
                        0,
                        {
                            "name": cls.product_tracking.name,
                            "product_id": cls.product_tracking.id,
                            "product_uom_qty": 6,
                            "product_uom": cls.product_tracking.uom_id.id,
                            "location_id": cls.stock_location.id,
                            "location_dest_id": cls.location_2.id,
                        },
                    )
                ],
            }
        )
        cls.option_group_quality_control = cls.env[
            "stock.barcodes.option.group"
        ].create(
            {
                "name": "Test option group control quality",
                "show_quality_control": True,
            }
        )
        cls.product_tracking.write(
            {
                "qc_triggers": [
                    (0, 0, {"trigger": cls.qc_trigger.id, "test": cls.test.id})
                ],
            }
        )
        cls.wiz_scan.picking_id = cls.picking_id.id
        cls.wiz_scan.option_group_id = cls.option_group_quality_control.id
        cls.wiz_quality_id = cls.WizardQualityControl.create({})
        cls.inspection1.picking_id = cls.picking_id.id
