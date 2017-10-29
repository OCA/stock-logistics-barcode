# coding: utf-8
# Copyright (C) 2017 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, models


class MobileAppInventory(models.Model):
    _name = 'mobile.app.inventory'

    # Public API Section
    @api.model
    def get_settings(self):
        """Return Mobile App Settings
        :return: {'key_1': value_1, 'key_2': value_2}
        """
        company = self.env.user.company_id
        return {
            'inventory_create': company.mobile_inventory_create,
        }

    @api.model
    def get_inventories(self):
        """Return Inventories available for the Mobile App
        :return: [inventory_1_vals, inventory_2_vals, ...]
        .. seealso:: _export_inventory() for inventory vals details.
        """
        inventory_obj = self.env['stock.inventory']
        inventories = inventory_obj.search(self._get_inventory_domain())
        return [
            self._export_inventory(inventory) for inventory in inventories]

    @api.model
    def get_locations(self, params):
        """ Return locations of a given inventory, or all locations available
        to realize an inventory, if inventory is not defined.
        :param params: {'inventory': inventory_1_vals}
        :return: [location_1_vals, location_2_vals, ...]
        .. seealso::
            _export_inventory() for inventory vals details
            _export_location() for location vals details
        """
        location_obj = self.env['stock.location']
        inventory_id = self._extract_param(params, 'inventory.id')
        locations = location_obj.search(
            self._get_location_domain(inventory_id))
        return [
            self._export_location(location) for location in locations]

    @api.model
    def get_inventory_lines(self, params):
        """ Return products of a given inventory. (products defined in all
        inventory lines of an inventory
        :param params: {'inventory': inventory_vals}
        :return: [product_1_vals, product_2_vals, ...]
        .. seealso::
            _export_inventory() for inventory vals details
            _export_product() for product vals details
        """
        inventory_obj = self.env['stock.inventory']
        inventory_id = self._extract_param(params, 'inventory.id')
        inventories = inventory_obj.browse(inventory_id)
        products = inventories.mapped('line_ids.product_id')
        # TODO : expected_qty, custom_fields
        return [
            self._export_product(product) for product in products]

    @api.model
    def search_barcode(self, params):
        """Realize a product, if found, given a barcode.
        :param params: {'barcode': string, 'location': location_vals}
        :return: product_1_vals
        .. seealso::
            _export_location() for location vals details
            _export_product() for product vals details
        """
        product_obj = self.env['product.product']
        product = self.search([('ean13', '=', barcode)])
        barcode_qty = 0
        if not product:
            product, barcode_qty = self.guess_product_qty(barcode)
#        if not product:
#            return False
#        res = product[0]._mobile_inventory_load_product()
#        res[0]['barcode_qty'] = qty
#        return res

    # Domain Section
    @api.model
    def _get_inventory_domain(self):
        return [('state', '=', 'confirm'), ('mobile_available', '=', True)]

    @api.model
    def _get_location_domain(self, inventory_id=False):
        inventory_obj = self.env['stock.inventory']
        domain = [('usage', '=', 'internal'), ('mobile_available', '=', True)]
        if inventory_id:
            parent_location = inventory_obj.browse(inventory_id).location_id
            domain += [('location_id', 'child_of', parent_location.id)]
        return domain

    # Export Section
    @api.model
    def _export_inventory(self, inventory):
        return {
            'id': inventory.id,
            'date': inventory.date,
            'name': inventory.name,
            'location': self._export_location(inventory.location_id),
        }

    @api.model
    def _export_location(self, location):
        return {
            'id': location.id,
            'name': location.name,
            'parent_complete_name': (
                location.location_id and
                location.location_id.display_name or False),
            'barcode': location.loc_barcode,
        }

    @api.model
    def _export_product(self, product, expected_qty=0, barcode_qty=0):
        custom_vals = []  # TODO
        return {
            'id': product.id,
            'name': product.name,
            'barcode': product.ean13,
            'barcode_qty': barcode_qty,
            'expected_qty': expected_qty,
            'custom_vals': custom_vals,
        }

    # Custom Section
    @api.model
    def _extract_param(self, params, value_path):
        if not type(params) is dict:
            return False
        obj = params.get(obj_name, False)
        if not obj:
            return False
        return obj.get('id', False)
