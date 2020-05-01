# Copyright 2020 Manuel Calero - Xtendoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.addons.stock_barcodes.tests.test_stock_barcodes import\
    TestStockBarcodes


class TestStockBarcodesInternalTransfer(TestStockBarcodes):
    def setUp(self):
        super().setUp()
        self.ScanReadInternalTransfer = self.env[
            'wiz.stock.barcodes.read.internal.transfer'
        ]
        self.stock_picking_model = self.env.ref('stock.model_stock_picking')

        # Model Data
        self.partner_agrolite = self.env.ref('base.res_partner_2')
        self.picking_type_in = self.env.ref('stock.picking_type_in')
        self.picking_type_out = self.env.ref('stock.picking_type_out')
        self.supplier_location = self.env.ref('stock.stock_location_suppliers')
        self.customer_location = self.env.ref('stock.stock_location_customers')
        self.stock_location = self.env.ref('stock.stock_location_stock')
        self.categ_unit = self.env.ref('uom.product_uom_categ_unit')
        self.categ_kgm = self.env.ref('uom.product_uom_categ_kgm')

        self.picking_in_01 = self.env['stock.picking'].with_context(
            planned_picking=True
        ).create({
            'location_id': self.supplier_location.id,
            'location_dest_id': self.stock_location.id,
            'partner_id': self.partner_agrolite.id,
            'picking_type_id': self.picking_type_in.id,
            'immediate_transfer': True,

        })
        self.picking_in_01.action_confirm()
        vals = self.picking_in_01.action_barcode_internal_transfer_scan()
        self.wiz_scan_internal_transfer = self.ScanReadInternalTransfer.with_context(
            vals['context']
        ).create({})

    def test_wiz_internal_transfer_values(self):
        self.assertEqual(self.wiz_scan_internal_transfer.location_id,
                         self.picking_in_01.location_id)
        self.assertEqual(self.wiz_scan_internal_transfer.location_dest_id,
                         self.picking_in_01.location_dest_id)
        self.assertEqual(self.wiz_scan_internal_transfer.res_model_id,
                         self.stock_picking_model)
        self.assertEqual(self.wiz_scan_internal_transfer.res_id,
                         self.picking_in_01.id)
        self.assertEqual(self.wiz_scan_internal_transfer.display_name,
                         'Barcode reader - %s - OdooBot' % (
                             self.picking_in_01.name))

    def test_wizard_internal_transfer_scan_product(self):
        self.action_barcode_scanned(self.wiz_scan_internal_transfer, '8480000723208')
        self.assertEqual(
            self.wiz_scan_internal_transfer.product_id, self.product_wo_tracking)
        sml = self.picking_in_01.move_line_ids.filtered(
            lambda x: x.product_id == self.product_wo_tracking)
        self.assertEqual(sml.qty_done, 1.0)
        # Scan product with tracking lot enable
        self.action_barcode_scanned(self.wiz_scan_internal_transfer, '8433281006850')
        sml = self.picking_in_01.move_line_ids.filtered(
            lambda x: x.product_id == self.product_tracking)
        self.assertEqual(sml.qty_done, 0.0)
        self.assertEqual(self.wiz_scan_internal_transfer.message,
                         'Barcode: 8433281006850 (Waiting for input lot)')
        # Scan a lot. Increment quantities if scan product or other lot from
        # this product
        self.action_barcode_scanned(self.wiz_scan_internal_transfer, '8411822222568')
        sml = self.picking_in_01.move_line_ids.filtered(
            lambda x: x.product_id == self.product_tracking and x.lot_id)
        self.assertEqual(sml.lot_id, self.lot_1)
        self.assertEqual(sml.qty_done, 1.0)
        self.action_barcode_scanned(self.wiz_scan_internal_transfer, '8433281006850')
        self.assertEqual(sml.qty_done, 2.0)
        self.action_barcode_scanned(self.wiz_scan_internal_transfer, '8411822222568')
        self.assertEqual(sml.qty_done, 3.0)
        self.assertEqual(self.wiz_scan_internal_transfer.message,
                         'Barcode: 8411822222568 (Barcode read correctly)')
        # Scan a package
        self.action_barcode_scanned(self.wiz_scan_internal_transfer, '5420008510489')
        # Package of 5 product units. Already three unit exists
        self.assertEqual(sml.qty_done, 8.0)

    def test_wizard_internal_transfer_scan_error_lot(self):
        # Scan product with tracking lot enable
        self.action_barcode_scanned(self.wiz_scan_internal_transfer, '8433281006850')
        sml = self.picking_in_01.move_line_ids.filtered(
            lambda x: x.product_id == self.product_tracking)
        self.assertEqual(sml.qty_done, 0.0)
        self.assertEqual(self.wiz_scan_internal_transfer.message,
                         'Barcode: 8433281006850 (Waiting for input lot)')
        # Scan a lot. Increment quantities if scan product or other lot from
        # this product
        self.action_barcode_scanned(self.wiz_scan_internal_transfer, '8411822222568')
        sml = self.picking_in_01.move_line_ids.filtered(
            lambda x: x.product_id == self.product_tracking and x.lot_id)
        self.assertEqual(sml.lot_id, self.lot_1)
        self.assertEqual(sml.qty_done, 1.0)
        # Scan an incorrect lot.
        self.action_barcode_scanned(self.wiz_scan_internal_transfer, '8488888888888')
        self.assertEqual(self.wiz_scan_internal_transfer.message,
                         'Barcode: 8488888888888 (Barcode not found)')

    def test_wizard_internal_transfer_scan_the_same_lot(self):
        # Scan product with tracking lot enable
        self.action_barcode_scanned(self.wiz_scan_internal_transfer, '8433281006850')
        sml = self.picking_in_01.move_line_ids.filtered(
            lambda x: x.product_id == self.product_tracking)
        self.assertEqual(sml.qty_done, 0.0)
        self.assertEqual(self.wiz_scan_internal_transfer.message,
                         'Barcode: 8433281006850 (Waiting for input lot)')
        # Scan a lot. Increment quantities if scan product or other lot from
        # this product
        self.action_barcode_scanned(self.wiz_scan_internal_transfer, '8411822222568')
        sml = self.picking_in_01.move_line_ids.filtered(
            lambda x: x.product_id == self.product_tracking and x.lot_id)
        self.assertEqual(sml.lot_id, self.lot_1)
        self.assertEqual(sml.qty_done, 1.0)
        # Scan the same lot.
        self.action_barcode_scanned(self.wiz_scan_internal_transfer, '8411822222568')
        self.assertEqual(sml.qty_done, 2.0)

    def test_wizard_internal_transfer_scan_product_manual_entry(self):
        self.wiz_scan_internal_transfer.manual_entry = True
        self.action_barcode_scanned(self.wiz_scan_internal_transfer, '8480000723208')
        self.assertEqual(self.wiz_scan_internal_transfer.product_id,
                         self.product_wo_tracking)
        self.assertEqual(self.wiz_scan_internal_transfer.product_qty, 0.0)
        self.wiz_scan_internal_transfer.product_qty = 12.0
        self.wiz_scan_internal_transfer.action_manual_entry()
        sml = self.picking_in_01.move_line_ids.filtered(
            lambda x: x.product_id == self.product_wo_tracking)
        self.assertEqual(sml.qty_done, 12.0)
        self.assertEqual(sml.move_id.quantity_done, 12.0)

    def test_wizard_internal_transfer_remove_last_scan(self):
        self.action_barcode_scanned(self.wiz_scan_internal_transfer, '8480000723208')
        self.assertEqual(self.wiz_scan_internal_transfer.product_id,
                         self.product_wo_tracking)
        sml = self.picking_in_01.move_line_ids.filtered(
            lambda x: x.product_id == self.product_wo_tracking)
        self.assertEqual(sml.qty_done, 1.0)
        self.wiz_scan_internal_transfer.action_undo_last_scan()
        self.assertEqual(sml.qty_done, 0.0)
        self.assertEqual(self.wiz_scan_internal_transfer.picking_product_qty, 0.0)
