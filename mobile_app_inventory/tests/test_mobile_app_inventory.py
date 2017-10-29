# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.tests import common


class TestMobileAppInventory(common.TransactionCase):
    """Tests for 'Mobile App Inventory' Module"""

    def setUp(self):
        super(TestMobileAppInventory, self).setUp()
        cr, uid = self.cr, self.uid
        self.chips_barcode = '5400313040109'

        self.app_obj = self.env['mobile.app.inventory']
        self.inventory_obj = self.env['stock.inventory']

        self.product_chips = self.env.ref(
            'mobile_app_inventory.product_chips_paprika')
        self.stock_location = self.env.ref('stock.stock_location_stock')

    def _get_inventory_single_line(self, inventory_id):
        """Private function that return the first line of an inventory
            or raise an error, if not found.
        """
        inventory = self.inventory_obj.browse(inventory_id)
        self.assertEqual(
            len(inventory.line_ids), 1,
            "Inventory line loading failed")
        return inventory.line_ids[0]

    # Test Section
    def test_01_load_section(self):
        """Test if data are correctly loaded for Mobile App"""
        data = self.app_obj.get_settings()
        self.assertEqual(
            type(data) is dict, True,
            "Loading Settings Datas should return a dict")

        data = self.app_obj.get_inventories()
        self.assertEqual(
            type(data) is list, True,
            "Loading Settings Datas should return a list")

        data = self.app_obj.get_locations({})
        self.assertEqual(
            type(data) is list, True,
            "Loading Settings Datas should return a list")

    def test_02_search_barcode(self):
        """Test if product custom datas are correctly loaded."""
        data = self.app_obj.search_barcode({'barcode': self.chips_barcode})
        self.assertEqual(
            type(data) is dict, True,
            "Loading product Datas should return product infos")

        self.assertEqual(
            data.get('name', False), self.product_chips.name,
            "Loading product datas should return base data. (name field)")

        self.assertEqual(
            data.get('custom_vals', {}).get('Sale Price', False),
            self.product_chips.list_price,
            "Loading product datas should return custom data."
            " defined in res.company settings (name list_price)")

    def test_03_create_inventory(self):
        """Test if inventory and lines are created correctly"""
        # Create Inventory
        inventory_data = self.app_obj.create_inventory(
            {'inventory': {'name': 'Test'}})

        self.assertNotEqual(
            type(inventory_data) is dict and inventory_data.get('id') or False,
            False, "Inventory creation failed by Mobile App")

        inventory_id = inventory_data['id']
        # Create new inventory Line
        self.app_obj.add_inventory_line({
            'inventory': {'id': inventory_data['id']},
            'location': {'id': self.stock_location.id},
            'product': {'id': self.product_chips.id},
            'qty': 10,
            'mode': 'ask',
        })
        line = self._get_inventory_single_line(inventory_id)
        self.assertEqual(
            line.product_id.id, self.product_chips.id,
            "Product is not correct in the new inventory line")
        self.assertEqual(
            line.location_id.id, self.stock_location.id,
            "Location is not correct in the new inventory line")
        self.assertEqual(
            line.product_qty, 10,
            "Quantity is not correct in the new inventory line")

        # Add same product (ask mode) and test
        self.app_obj.add_inventory_line({
            'inventory': {'id': inventory_data['id']},
            'location': {'id': self.stock_location.id},
            'product': {'id': self.product_chips.id},
            'qty': 11,
            'mode': 'ask',
        })
        line = self._get_inventory_single_line(inventory_id)
        self.assertEqual(
            line.product_qty, 10,
            "Quantity for duplicate lines should not change in ask mode")

        # Add same product (replace mode) and test
        self.app_obj.add_inventory_line({
            'inventory': {'id': inventory_data['id']},
            'location': {'id': self.stock_location.id},
            'product': {'id': self.product_chips.id},
            'qty': 30,
            'mode': 'replace',
        })

        line = self._get_inventory_single_line(inventory_id)
        self.assertEqual(
            line.product_qty, 30,
            "Quantity for duplicate lines should be replaced in replace mode")

        # Add same product (add mode) and test
        self.app_obj.add_inventory_line({
            'inventory': {'id': inventory_data['id']},
            'location': {'id': self.stock_location.id},
            'product': {'id': self.product_chips.id},
            'qty': 70,
            'mode': 'add',
        })

        line = self._get_inventory_single_line(inventory_id)
        self.assertEqual(
            line.product_qty, 100,
            "Quantity for duplicate lines should be added in add mode")
