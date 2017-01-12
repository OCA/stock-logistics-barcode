# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.tests.common import TransactionCase


class TestScanToInventory(TransactionCase):
    """Tests for 'Scan To Inventory' Module"""

    def setUp(self):
        super(TestScanToInventory, self).setUp()
        cr, uid = self.cr, self.uid
        self.test_barcode = '5400313040109'

        self.model_data_obj = self.registry('ir.model.data')
        self.product_obj = self.registry('product.product')
        self.inventory_obj = self.registry('stock.inventory')
        self.location_obj = self.registry('stock.location')

        self.product_id = self.model_data_obj.get_object_reference(
            cr, uid, 'mobile_app_inventory', 'product_chips_paprika')[1]
        self.location_id = self.model_data_obj.get_object_reference(
            cr, uid, 'stock', 'stock_location_stock')[1]

    def _get_inventory_single_line(self, inventory_id):
        """Private function that return the first line of an inventory
            or raise an error, if not found.
        """
        cr, uid = self.cr, self.uid
        inventory = self.inventory_obj.browse(cr, uid, inventory_id)
        self.assertEqual(
            len(inventory.inventory_line_id), 1,
            "Inventory line loading failed")
        return inventory.inventory_line_id[0]

    # Test Section
    def test_01_load_custom(self):
        """Test if product custom datas are correctly loaded."""
        cr, uid = self.cr, self.uid
        self.product_obj.write(cr, uid, [self.product_id], {
            'ean13': self.test_barcode,
        })
        product = self.product_obj.browse(cr, uid, self.product_id)
        res = self.product_obj.mobile_app_inventory_load_product(cr, uid)
        self.assertEqual(
            self.test_barcode in res, True,
            "Loading product Datas should return product with barcode")
        data = res.get(self.test_barcode, False)
        self.assertEqual(
            data.get('name', False), product.name,
            "Loading product datas should return base data. (name field)")
        self.assertEqual(
            data.get('list_price', {}).get('value', False),
            product.list_price,
            "Loading product datas should return custom data."
            " defined in res.company settings (name list_price)")

    # Test Section
    def test_02_create_inventory(self):
        """Test if inventory is created correctly."""
        cr, uid = self.cr, self.uid

        # Create Inventory and test
        inventory_id = self.inventory_obj.create_by_scan(
            cr, uid, 'mobile_app_inventory test')

        self.assertNotEqual(
            inventory_id, False,
            "Inventory creation failed by UI")

        # Create new inventory Line and test
        self.inventory_obj.add_inventory_line_by_scan(
            cr, uid, inventory_id, self.location_id, self.product_id, 10,
            'ask')
        line = self._get_inventory_single_line(inventory_id)
        self.assertEqual(
            line.product_id.id, self.product_id,
            "Product is not correct in the new inventory line")
        self.assertEqual(
            line.location_id.id, self.location_id,
            "Location is not correct in the new inventory line")
        self.assertEqual(
            line.product_qty, 10,
            "Quantity is not correct in the new inventory line")

        # Add same product (ask mode) and test
        self.inventory_obj.add_inventory_line_by_scan(
            cr, uid, inventory_id, self.location_id, self.product_id, 11,
            'ask')
        line = self._get_inventory_single_line(inventory_id)
        self.assertEqual(
            line.product_qty, 10,
            "Quantity for duplicate lines should not change in ask mode")

        # Add same product (replace mode) and test
        self.inventory_obj.add_inventory_line_by_scan(
            cr, uid, inventory_id, self.location_id, self.product_id, 30,
            'replace')
        line = self._get_inventory_single_line(inventory_id)
        self.assertEqual(
            line.product_qty, 30,
            "Quantity for duplicate lines should be replaced in replace mode")

        # Add same product (add mode) and test
        self.inventory_obj.add_inventory_line_by_scan(
            cr, uid, inventory_id, self.location_id, self.product_id, 70,
            'add')
        line = self._get_inventory_single_line(inventory_id)
        self.assertEqual(
            line.product_qty, 100,
            "Quantity for duplicate lines should be added in add mode")
