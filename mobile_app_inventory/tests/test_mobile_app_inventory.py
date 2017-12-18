# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests import common


class TestMobileAppInventory(common.TransactionCase):
    """Tests for 'Mobile App Inventory' Module"""

    def setUp(self):
        super(TestMobileAppInventory, self).setUp()
        self.chips_barcode = '5400313040109'

        self.app_obj = self.env['mobile.app.inventory']
        self.inventory_obj = self.env['stock.inventory']

        self.product_chips = self.env.ref(
            'mobile_app_inventory.product_chips_paprika')
        self.stock_location = self.env.ref('stock.stock_location_stock')

        self.shelf_2_inventory = self.env.ref(
            'mobile_app_inventory.shelf_2_inventory')

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
        json_inventory = self.app_obj.create_inventory(
            {'inventory': {'name': 'Test'}})

        self.assertNotEqual(
            type(json_inventory) is dict and json_inventory.get('id') or False,
            False, "Inventory creation failed by Mobile App")

        inventory_id = json_inventory['id']
        # Create new inventory Line
        self.app_obj.add_inventory_line({
            'inventory': {'id': json_inventory['id']},
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
            'inventory': {'id': json_inventory['id']},
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
            'inventory': {'id': json_inventory['id']},
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
            'inventory': {'id': json_inventory['id']},
            'location': {'id': self.stock_location.id},
            'product': {'id': self.product_chips.id},
            'qty': 70,
            'mode': 'add',
        })

        line = self._get_inventory_single_line(inventory_id)
        self.assertEqual(
            line.product_qty, 100,
            "Quantity for duplicate lines should be added in add mode")

    def test_04_get_inventories_after_creation(self):
        """It should return updated list of available inventories"""

        data_1 = self.app_obj.get_inventories()
        self.app_obj.create_inventory(
            {'inventory': {'name': 'Test'}})
        data_2 = self.app_obj.get_inventories()
        self.assertEqual(
            len(data_1), len(data_2) - 1,
            "created inventories should be available")

    def test_05_child_of_location(self):
        """It should only return child of location."""
        list_full = self.app_obj.get_locations({})
        list_sub = self.app_obj.get_locations(
            {'inventory': {'id': self.shelf_2_inventory.id}})
        self.assertGreater(
            len(list_full), len(list_sub),
            "Getting available locations of an inventory should"
            " return only sub locations of the main location of the inventory")

    def test_06_unkown_product_id(self):
        """Test adding inventory line via barcode product"""
        json_inventory = self.app_obj.create_inventory(
            {'inventory': {'name': 'Test'}})

        res = self.app_obj.add_inventory_line({
            'inventory': {'id': json_inventory['id']},
            'location': {'id': self.stock_location.id},
            'product': {'barcode': '5400313040109'},
            'qty': 3,
            'mode': 'ask',
        })
        self.assertEqual(
            type(res) == dict and res.get('state', False) or False, 'write_ok',
            "Adding inventory line via barcode should works")

    def test_07_unkown_barcode(self):
        """Test adding unknown inventory line via unknown barcode"""
        json_inventory = self.app_obj.create_inventory(
            {'inventory': {'name': 'Test'}})

        self.app_obj.add_inventory_line({
            'inventory': {'id': json_inventory['id']},
            'location': {'id': self.stock_location.id},
            'product': {'barcode': '1234567890123'},
            'qty': 10,
            'mode': 'ask',
        })
        inventory = self.inventory_obj.browse(json_inventory['id'])
        self.assertEqual(
            inventory.unknown_line_qty, 1,
            "Scanning unknown barcode should create a new unknown line")

        self.assertEqual(
            inventory.unknown_line_ids[0].barcode, '1234567890123',
            "Scanning unknown barcode should create a new unknown line"
            " with the according barcode")

        self.assertEqual(
            inventory.unknown_line_ids[0].quantity, 10,
            "Scanning unknown barcode should create a new unknown line"
            " with the according quantity")
