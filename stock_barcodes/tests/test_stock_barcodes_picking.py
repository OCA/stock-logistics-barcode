# Copyright 2108-2019 Sergio Teruel <sergio.teruel@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.addons.stock_barcodes.tests.test_stock_barcodes import\
    TestStockBarcodes
from lxml import etree


class TestStockBarcodesPicking(TestStockBarcodes):
    def setUp(self):
        super().setUp()
        self.ScanReadPicking = self.env['wiz.stock.barcodes.read.picking']
        self.stock_picking_model = self.env.ref('stock.model_stock_picking')

        # Model Data
        self.partner_agrolite = self.env.ref('base.res_partner_2')
        self.picking_type_in = self.env.ref('stock.picking_type_in')
        self.picking_type_out = self.env.ref('stock.picking_type_out')
        self.picking_type_internal = self.env.ref('stock.picking_type_internal')
        self.supplier_location = self.env.ref('stock.stock_location_suppliers')
        self.customer_location = self.env.ref('stock.stock_location_customers')
        self.stock_location = self.env.ref('stock.stock_location_stock')
        self.pack_location = self.env.ref('stock.location_pack_zone')
        self.categ_unit = self.env.ref('uom.product_uom_categ_unit')
        self.categ_kgm = self.env.ref('uom.product_uom_categ_kgm')
        self.picking_out_01 = self.env['stock.picking'].with_context(
            planned_picking=True
        ).create({
            'location_id': self.stock_location.id,
            'location_dest_id': self.customer_location.id,
            'partner_id': self.partner_agrolite.id,
            'picking_type_id': self.picking_type_out.id,
            'move_lines': [
                (0, 0, {
                    'name': self.product_tracking.name,
                    'product_id': self.product_tracking.id,
                    'product_uom_qty': 3,
                    'product_uom': self.product_tracking.uom_id.id,
                    'location_id': self.stock_location.id,
                    'location_dest_id': self.customer_location.id,
                }),
            ]
        })
        self.picking_out_02 = self.picking_out_01.copy()
        self.picking_in_01 = self.env['stock.picking'].with_context(
            planned_picking=True
        ).create({
            'location_id': self.supplier_location.id,
            'location_dest_id': self.stock_location.id,
            'partner_id': self.partner_agrolite.id,
            'picking_type_id': self.picking_type_in.id,
            'move_lines': [
                (0, 0, {
                    'name': self.product_wo_tracking.name,
                    'product_id': self.product_wo_tracking.id,
                    'product_uom_qty': 3,
                    'product_uom': self.product_wo_tracking.uom_id.id,
                    'location_id': self.supplier_location.id,
                    'location_dest_id': self.stock_location.id,
                }),
                (0, 0, {
                    'name': self.product_wo_tracking.name,
                    'product_id': self.product_wo_tracking.id,
                    'product_uom_qty': 5,
                    'product_uom': self.product_wo_tracking.uom_id.id,
                    'location_id': self.supplier_location.id,
                    'location_dest_id': self.stock_location.id,
                }),
                (0, 0, {
                    'name': self.product_tracking.name,
                    'product_id': self.product_tracking.id,
                    'product_uom_qty': 3,
                    'product_uom': self.product_tracking.uom_id.id,
                    'location_id': self.supplier_location.id,
                    'location_dest_id': self.stock_location.id,
                }),
                (0, 0, {
                    'name': self.product_tracking.name,
                    'product_id': self.product_tracking.id,
                    'product_uom_qty': 5,
                    'product_uom': self.product_tracking.uom_id.id,
                    'location_id': self.supplier_location.id,
                    'location_dest_id': self.stock_location.id,
                }),
            ]
        })
        self.picking_in_01.action_confirm()
        vals = self.picking_in_01.action_barcode_scan()
        self.wiz_scan_picking = self.ScanReadPicking.with_context(
            vals['context']
        ).create({})
        # Create a wizard for outgoing picking
        self.picking_out_01.action_confirm()
        vals = self.picking_out_01.action_barcode_scan()
        self.wiz_scan_picking_out = self.ScanReadPicking.with_context(
            vals['context']
        ).create({})

    def test_wiz_picking_values(self):
        self.assertEqual(self.wiz_scan_picking.location_id,
                         self.picking_in_01.location_dest_id)
        self.assertEqual(self.wiz_scan_picking.res_model_id,
                         self.stock_picking_model)
        self.assertEqual(self.wiz_scan_picking.res_id,
                         self.picking_in_01.id)
        self.assertIn(
            "Barcode reader - %s - " % (self.picking_in_01.name),
            self.wiz_scan_picking.display_name,
        )

    def test_picking_wizard_scan_product(self):
        self.action_barcode_scanned(self.wiz_scan_picking, '8480000723208')
        self.assertEqual(
            self.wiz_scan_picking.product_id, self.product_wo_tracking)
        sml = self.picking_in_01.move_line_ids.filtered(
            lambda x: x.product_id == self.product_wo_tracking)
        self.assertEqual(sml.qty_done, 1.0)
        # Scan product with tracking lot enable
        self.action_barcode_scanned(self.wiz_scan_picking, '8433281006850')
        sml = self.picking_in_01.move_line_ids.filtered(
            lambda x: x.product_id == self.product_tracking)
        self.assertEqual(sml.qty_done, 0.0)
        self.assertEqual(self.wiz_scan_picking.message,
                         'Barcode: 8433281006850 (Waiting for input lot)')
        # Scan a lot. Increment quantities if scan product or other lot from
        # this product
        self.action_barcode_scanned(self.wiz_scan_picking, '8411822222568')
        sml = self.picking_in_01.move_line_ids.filtered(
            lambda x: x.product_id == self.product_tracking and x.lot_id)
        self.assertEqual(sml.lot_id, self.lot_1)
        self.assertEqual(sml.qty_done, 1.0)
        self.action_barcode_scanned(self.wiz_scan_picking, '8433281006850')
        self.assertEqual(sml.qty_done, 2.0)
        self.action_barcode_scanned(self.wiz_scan_picking, '8411822222568')
        self.assertEqual(sml.qty_done, 3.0)
        self.assertEqual(self.wiz_scan_picking.message,
                         'Barcode: 8411822222568 (Barcode read correctly)')
        # Scan a package
        self.action_barcode_scanned(self.wiz_scan_picking, '5420008510489')
        # Package of 5 product units. Already three unit exists
        self.assertEqual(sml.qty_done, 8.0)

    def test_compute_pending_products(self):
        self.assertTrue(self.wiz_scan_picking.pending_moves)
        for i in range(0, 8):
            view = etree.fromstring(self.wiz_scan_picking.pending_moves)
            node = view.xpath("//table/tr/td/span[text() = '%s']/../.."
                              % self.product_tracking.display_name)
            self.assertTrue(node)
            quantity_done = node[0].xpath('td[last()]/span')
            self.assertEqual(i, float(quantity_done[0].text))
            node = view.xpath("//table/tr/td/span[text() = '%s']/../.."
                              % self.product_wo_tracking.display_name)
            self.assertTrue(node)
            quantity_done = node[0].xpath('td[last()]/span')
            self.assertEqual(0, float(quantity_done[0].text))
            self.action_barcode_scanned(self.wiz_scan_picking, '8411822222568')
        view = etree.fromstring(self.wiz_scan_picking.pending_moves)
        node = view.xpath("//table/tr/td/span[text() = '%s']/../.."
                          % self.product_tracking.display_name)
        self.assertFalse(node)
        node = view.xpath("//table/tr/td/span[text() = '%s']/../.."
                          % self.product_wo_tracking.display_name)
        self.assertTrue(node)
        quantity_done = node[0].xpath('td[last()]/span')
        self.assertEqual(0, float(quantity_done[0].text))
        move = self.wiz_scan_picking.picking_id.move_ids_without_package.\
            filtered(
                lambda r: r.product_id == self.product_wo_tracking)
        move.quantity_done = move.product_uom_qty
        self.assertRegex(self.wiz_scan_picking.pending_moves,
                         ".*No pending operations.*")

    def test_picking_wizard_scan_product_manual_entry(self):
        self.wiz_scan_picking.manual_entry = True
        self.action_barcode_scanned(self.wiz_scan_picking, '8480000723208')
        self.assertEqual(self.wiz_scan_picking.product_id,
                         self.product_wo_tracking)
        sml = self.picking_in_01.move_line_ids.filtered(
            lambda x: x.product_id == self.product_wo_tracking)
        self.assertEqual(self.wiz_scan_picking.product_qty, 0.0)
        self.wiz_scan_picking.product_qty = 12.0
        self.wiz_scan_picking.action_manual_entry()
        self.assertEqual(sml.qty_done, 8.0)
        self.assertEqual(sml.move_id.quantity_done, 12.0)

    def test_picking_wizard_remove_last_scan(self):
        self.action_barcode_scanned(self.wiz_scan_picking, '8480000723208')
        self.assertEqual(self.wiz_scan_picking.product_id,
                         self.product_wo_tracking)
        sml = self.picking_in_01.move_line_ids.filtered(
            lambda x: x.product_id == self.product_wo_tracking)
        self.assertEqual(sml.qty_done, 1.0)
        self.wiz_scan_picking.action_undo_last_scan()
        self.assertEqual(sml.qty_done, 0.0)
        self.assertEqual(self.wiz_scan_picking.picking_product_qty, 0.0)

    def test_barcode_from_operation(self):
        picking_out_3 = self.picking_out_01.copy()
        self.picking_out_01.action_assign()
        self.picking_out_02.action_assign()

        vals = self.picking_type_out.action_barcode_scan()
        self.wiz_scan_picking = self.ScanReadPicking.with_context(
            vals['context']
        ).create({})
        self.wiz_scan_picking.manual_entry = True
        self.wiz_scan_picking.product_id = self.product_tracking
        self.wiz_scan_picking.lot_id = self.lot_1
        self.wiz_scan_picking.product_qty = 2

        self.wiz_scan_picking.action_manual_entry()
        self.assertEqual(len(self.wiz_scan_picking.candidate_picking_ids), 2)
        # Lock first picking
        candidate = self.wiz_scan_picking.candidate_picking_ids.filtered(
            lambda c: c.picking_id == self.picking_out_01)
        candidate_wiz = candidate.with_context(
            wiz_barcode_id=self.wiz_scan_picking.id,
            picking_id=self.picking_out_01.id,
        )
        candidate_wiz.action_lock_picking()
        self.assertEqual(self.picking_out_01.move_lines.quantity_done, 2)
        self.wiz_scan_picking.action_manual_entry()
        self.assertEqual(self.picking_out_01.move_lines.quantity_done, 4)

        # Picking out 3 is in confirmed state, so until confirmed moves has
        # not been activated candidate pickings is 2
        picking_out_3.action_confirm()
        candidate_wiz.action_unlock_picking()
        self.wiz_scan_picking.action_manual_entry()
        self.assertEqual(len(self.wiz_scan_picking.candidate_picking_ids), 2)
        self.wiz_scan_picking.confirmed_moves = True
        candidate_wiz.action_unlock_picking()
        self.wiz_scan_picking.action_manual_entry()
        self.assertEqual(len(self.wiz_scan_picking.candidate_picking_ids), 3)

    def test_picking_wizard_scan_product_auto_lot(self):
        # Prepare more data
        lot_2 = self.StockProductionLot.create({
            'name': '8411822222578',
            'product_id': self.product_tracking.id,
        })
        lot_3 = self.StockProductionLot.create({
            'name': '8411822222588',
            'product_id': self.product_tracking.id,
        })
        quant_lot_2 = self.StockQuant.create({
            'product_id': self.product_tracking.id,
            'lot_id': lot_2.id,
            'location_id': self.stock_location.id,
            'quantity': 15.0,
        })
        quant_lot_3 = self.StockQuant.create({
            'product_id': self.product_tracking.id,
            'lot_id': lot_3.id,
            'location_id': self.stock_location.id,
            'quantity': 10.0,
        })
        self.quant_lot_1.in_date = "2021-01-01"
        quant_lot_2.in_date = "2021-01-05"
        quant_lot_3.in_date = "2021-01-06"
        # Scan product with tracking lot enable
        self.action_barcode_scanned(self.wiz_scan_picking, '8433281006850')
        self.assertEqual(self.wiz_scan_picking.message,
                         'Barcode: 8433281006850 (Waiting for input lot)')

        self.wiz_scan_picking.auto_lot = True
        # self.wiz_scan_picking.manual_entry = True

        # Removal strategy FIFO

        # No auto lot for incoming pickings
        self.action_barcode_scanned(self.wiz_scan_picking, '8433281006850')
        self.assertFalse(self.wiz_scan_picking.lot_id)

        # Continue test with a outgoing wizard
        self.wiz_scan_picking_out.auto_lot = True
        self.action_barcode_scanned(self.wiz_scan_picking_out, '8433281006850')
        self.assertEqual(self.wiz_scan_picking_out.lot_id, self.lot_1)

        # Removal strategy LIFO
        self.wiz_scan_picking_out.lot_id = False
        self.product_tracking.categ_id.removal_strategy_id = self.env.ref(
            "stock.removal_lifo")
        self.action_barcode_scanned(self.wiz_scan_picking_out, '8433281006850')
        self.assertEqual(self.wiz_scan_picking_out.lot_id, lot_3)

    def test_picking_package(self):
        self.StockQuant.create({
            'product_id': self.product_wo_tracking.id,
            'location_id': self.stock_location.id,
            'quantity': 100.0,
        })
        self.pack_location.active = True
        packing_picking = self.env['stock.picking'].with_context(
            planned_picking=True
        ).create({
            'location_id': self.stock_location.id,
            'location_dest_id': self.pack_location.id,
            'picking_type_id': self.picking_type_internal.id,
            'move_lines': [
                (0, 0, {
                    'name': self.product_wo_tracking.name,
                    'product_id': self.product_wo_tracking.id,
                    'product_uom_qty': 2,
                    'product_uom': self.product_wo_tracking.uom_id.id,
                    'location_id': self.stock_location.id,
                    'location_dest_id': self.pack_location.id,
                }),
            ]
        })
        packing_picking.action_assign()
        vals = packing_picking.action_barcode_scan()
        vals['context']['picking_id'] = packing_picking.id
        wiz_scan_picking = self.ScanReadPicking.with_context(
            vals['context']
        ).create({})
        self.action_barcode_scanned(wiz_scan_picking, '8480000723208')
        self.action_barcode_scanned(wiz_scan_picking, '8480000723208')
        wiz_scan_picking.put_in_pack()
        wiz_scan_picking.candidate_picking_ids[0].action_validate_picking()
        package = packing_picking.move_line_ids[0].result_package_id
        self.assertEqual(packing_picking.state, 'done')
        self.assertEqual(
            packing_picking.move_line_ids[0].result_package_id.location_id.id,
            self.pack_location.id)
        self.assertEqual(packing_picking.move_line_ids[0].qty_done, 2)

        out_picking = self.env['stock.picking'].with_context(
            planned_picking=True
        ).create({
            'location_id': self.pack_location.id,
            'location_dest_id': self.customer_location.id,
            'partner_id': self.partner_agrolite.id,
            'picking_type_id': self.picking_type_out.id,
            'move_lines': [
                (0, 0, {
                    'name': self.product_wo_tracking.name,
                    'product_id': self.product_wo_tracking.id,
                    'product_uom_qty': 2,
                    'product_uom': self.product_wo_tracking.uom_id.id,
                    'location_id': self.pack_location.id,
                    'location_dest_id': self.customer_location.id,
                }),
            ]
        })

        out_picking.action_assign()
        self.assertEqual(package.id, out_picking.move_line_ids[0].package_id.id)
        vals = out_picking.action_barcode_scan()
        vals['context']['picking_id'] = out_picking.id
        wiz_scan_picking = self.ScanReadPicking.with_context(
            vals['context']
        ).create({})
        self.action_barcode_scanned(wiz_scan_picking, package.name)
        self.assertEqual(out_picking.move_line_ids[0].qty_done, 2)
        wiz_scan_picking.candidate_picking_ids[0].action_validate_picking()
        self.assertEqual(out_picking.state, 'done')
