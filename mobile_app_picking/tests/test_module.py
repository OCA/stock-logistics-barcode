# Copyright (C) 2019-Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class TestModule(TransactionCase):

    def setUp(self):
        super().setUp()
        self.MobileAppPicking = self.env['mobile.app.picking']
        self.StockPicking = self.env['stock.picking']
        self.pickingTypeDemo = self.env.ref('stock.picking_type_in')
        self.pickingDemo = self.env.ref('mobile_app_picking.picking_in_A')
        self.moveDemo = self.env.ref('mobile_app_picking.move_A_1')

    # Test Section
    def test_main_scenario(self):
        # Load Picking Types, calling API
        items = self.MobileAppPicking.get_picking_types()

        # Search Demo Picking type
        pickingTypeJson = False
        for item in items:
            if item.get('id', False) == self.pickingTypeDemo.id:
                pickingTypeJson = item
        self.assertNotEqual(pickingTypeJson, False, "Picking Type not found")

        # Load Pickings, calling API
        items = self.MobileAppPicking.get_pickings(
            {'picking_type': pickingTypeJson})

        # Search Demo Picking
        pickingJson = False
        for item in items:
            if item.get('id', False) == self.pickingDemo.id:
                pickingJson = item
        self.assertNotEqual(pickingJson, False, "Picking not found")

        # Load Pickings, calling API
        items = self.MobileAppPicking.get_moves(
            {'picking': pickingJson})

        moveJson = False
        for item in items:
            if item.get('id', False) == self.moveDemo.id:
                moveJson = item

        self.assertNotEqual(moveJson, False, "Move not Found")
        self.assertEqual(len(items), 3, "Picking moves not loaded")

        # Set Quantity to 20 (30 forcasted)
        self.MobileAppPicking.set_quantity(
            {'move': moveJson, 'qty_done': 20})

        self.assertEqual(
            self.moveDemo.quantity_done, 20, "changing quantity failed")

        # Ask state of picking
        res = self.MobileAppPicking.try_validate_picking(
            {'picking': pickingJson})

        self.assertEqual(
            res, 'backorder_confirmation',
            "confirming partialy done picking should propose backorder")

        self.MobileAppPicking.confirm_picking(
            {'picking': pickingJson, 'action': 'with_backorder'})

        # Search backorder
        backorderPickings = self.StockPicking.search(
            [('backorder_id', '=', self.pickingDemo.id)])

        self.assertEqual(
            len(backorderPickings), 1, "Backorder should be generated")
