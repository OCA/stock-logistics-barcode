# Copyright 2026 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.tests import Form, tagged

from .test_scan_uom import ScanUomCommon


@tagged("post_install", "-at_install")
class TestScanOwner(ScanUomCommon):
    def test_selected_owner_reservation_and_validation(self):
        product = self.Product.create(
            {"name": "Consigned product", "barcode": "OWNER-SCAN", "is_storable": True}
        )
        owners = self.env["res.partner"].create(
            [{"name": "Stock owner A"}, {"name": "Stock owner B"}]
        )
        for owner in owners:
            self.StockQuant._update_available_quantity(
                product, self.location_1, 1, owner_id=owner
            )
        picking, wizard = self._scan_picking(product, 2, self.unit, incoming=False)
        wizard.manual_entry = True
        self.action_barcode_scanned(wizard, product.barcode)
        wizard.owner_id = owners[1]
        wizard.product_qty = 1
        self.assertEqual(wizard.qty_available, 1)
        wizard.action_confirm()
        scanned = picking.move_line_ids.filtered("qty_picked")
        self.assertEqual(scanned.owner_id, owners[1])
        self.assertEqual(scanned.qty_picked, 1)
        action = picking.with_context(
            stock_barcodes_read_picking_id=wizard.id
        ).button_validate()
        backorder = Form(
            self.env[action["res_model"]].with_context(**action["context"])
        ).save()
        backorder.process_cancel_backorder()
        self.assertEqual(picking.state, "done")
        self.assertEqual(picking.move_line_ids.owner_id, owners[1])
        self.assertEqual(picking.move_line_ids.quantity, 1)
        source_quants = self.StockQuant.search(
            [("product_id", "=", product.id), ("location_id", "=", self.location_1.id)]
        )
        self.assertEqual(
            sum(
                source_quants.filtered_domain([("owner_id", "=", owners[0].id)]).mapped(
                    "quantity"
                )
            ),
            1,
        )
        self.assertEqual(
            sum(
                source_quants.filtered_domain([("owner_id", "=", owners[1].id)]).mapped(
                    "quantity"
                )
            ),
            0,
        )
