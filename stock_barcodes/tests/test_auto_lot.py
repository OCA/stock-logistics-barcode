# Copyright 2026 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.tests import tagged

from .test_scan_uom import ScanUomCommon


@tagged("post_install", "-at_install")
class TestAutoLot(ScanUomCommon):
    def test_auto_lot_uses_own_fully_reserved_stock(self):
        self.scan_options.auto_lot = True
        product = self.Product.create(
            {
                "name": "Reserved lot scan",
                "barcode": "AUTO-RESERVED-LOT",
                "is_storable": True,
                "tracking": "lot",
                "uom_id": self.unit.id,
                "uom_po_id": self.unit.id,
            }
        )
        lot = self.StockProductionLot.create(
            {
                "name": "RESERVED-LOT",
                "product_id": product.id,
                "company_id": self.company.id,
            }
        )
        self.StockQuant._update_available_quantity(
            product, self.location_1, 2, lot_id=lot
        )
        picking, wizard = self._scan_picking(product, 2, self.unit, incoming=False)
        self.assertEqual(picking.move_line_ids.lot_id, lot)
        quants = self.StockQuant._gather(product, self.location_1, lot_id=lot)
        self.assertEqual(sum(quants.mapped("available_quantity")), 0)
        self.action_barcode_scanned(wizard, product.barcode)
        self.assertEqual(picking.move_ids.qty_picked, 1)
        self.assertEqual(picking.move_line_ids.lot_id, lot)
        self.action_barcode_scanned(wizard, product.barcode)
        self.assertEqual(picking.move_ids.qty_picked, 2)
        wizard.action_validate_picking()
        self.assertEqual(picking.state, "done")
        self.assertEqual(picking.move_line_ids.lot_id, lot)

    def test_auto_lot_does_not_take_another_pickings_reservation(self):
        self.scan_options.auto_lot = True
        product = self.Product.create(
            {
                "name": "Separate reserved lots",
                "barcode": "AUTO-SEPARATE-LOTS",
                "is_storable": True,
                "tracking": "lot",
            }
        )
        lots = self.StockProductionLot.create(
            [
                {"name": name, "product_id": product.id, "company_id": self.company.id}
                for name in ("FIRST-RESERVATION", "SECOND-RESERVATION")
            ]
        )
        self.StockQuant._update_available_quantity(
            product, self.location_1, 1, lot_id=lots[0]
        )
        other_picking, _wizard = self._scan_picking(
            product, 1, self.unit, incoming=False
        )
        self.StockQuant._update_available_quantity(
            product, self.location_1, 1, lot_id=lots[1]
        )
        picking, wizard = self._scan_picking(product, 1, self.unit, incoming=False)
        self.action_barcode_scanned(wizard, product.barcode)
        self.assertEqual(picking.move_ids.qty_picked, 1)
        self.assertEqual(picking.move_line_ids.lot_id, lots[1])
        self.assertFalse(other_picking.move_ids.qty_picked)
        wizard.action_validate_picking()
        self.assertEqual(picking.state, "done")
