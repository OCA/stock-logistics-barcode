# coding: utf-8
# Copyright (C) 2017 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import _, api, models


class MobileAppInventory(models.Model):
    _name = 'mobile.app.inventory'

    # Public API Section
    @api.model
    def check_group(self, group_ext_id):
        return self.env.user.has_group(group_ext_id)

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
    def create_inventory(self, params):
        """Create a new inventory, and set it to 'In Progress' State.
        :param params: {'inventory': inventory_vals}
        :return: inventory_vals
        .. seealso::
            _export_inventory() for inventory vals details
        """
        inventory_obj = self.env['stock.inventory']
        inventory_name = self._extract_param(params, 'inventory.name')
        vals = inventory_obj.default_get(self._defaults.keys())
        vals.update({
            'name': _('%s (Mobile App)') % (inventory_name),
            'filter': 'partial',
        })
        inventory = inventory_obj.create(vals)
        inventory.prepare_inventory()
        return self._export_inventory(inventory)

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
        """ Return inventory lines of a given inventory.
        :param params: {'inventory': inventory_vals}
        :return: [inventory_line_1_vals, inventory_line_2_vals, ...]
        .. seealso::
            _export_inventory() for inventory vals details
            _export_inventory_line() for inventory line vals details
        """
        inventory_obj = self.env['stock.inventory']
        inventory_id = self._extract_param(params, 'inventory.id')
        inventories = inventory_obj.browse(inventory_id)
        lines = inventories.line_ids.filtered(
            lambda line: line.product_id.ean13)
        custom_fields = self._get_custom_fields()
        return [
            self._export_inventory_line(line, custom_fields) for line in lines]

    @api.model
    def search_barcode(self, params):
        """Realize a product, if found, given a barcode.
        :param params: {'barcode': string, 'location': location_vals}
        :return: product_1_vals
        .. seealso::
            _export_location() for location vals details
            _export_product() for product vals details
        """
        barcode = self._extract_param(params, 'barcode')
        (product, barcode_qty) = self._search_barcode(barcode)
        if not product:
            return False
        else:
            custom_fields = self._get_custom_fields()
            return self._export_product(
                product, custom_fields, barcode_qty=barcode_qty)

    @api.model
    def add_inventory_line(self, params):
        """
        Add a new inventory line.
        :param params: {
            'inventory': inventory_vals, 'location': location_vals,
            'product': product_vals, 'qty': qty, 'mode': mode}
        @qty : the quantity to set or to add depending of the mode;
        @mode :
            'ask': Do nothing if there is a duplicate line;
            'add': Add quantity to the duplicate line;
            'replace': Replace quantity of the duplicate line;
        return:
            {'state': 'write_ok'}:
                Update / creation OK
            {'state': 'many_duplicate_lines'}:
                Too many duplicate lines. not possible to process
            {'state': 'duplicate', qty: xxx}:
                There is a duplicate. Qty is the current quantity
        """

        inventory_obj = self.env['stock.inventory']
        line_obj = self.env['stock.inventory.line']
        product_obj = self.env['product.product']
        inventory_id = self._extract_param(params, 'inventory.id')
        location_id = self._extract_param(params, 'location.id')
        product_id = self._extract_param(params, 'product.id')
        barcode = self._extract_param(params, 'product.barcode')
        qty = self._extract_param(params, 'qty')
        mode = self._extract_param(params, 'mode')
        inventory = inventory_obj.browse(inventory_id)
        qty = qty and float(qty) or 0.0
        product = False
        if product_id:
            product = product_obj.browse(product_id)
        elif barcode:
            (product, barcode_qty) = self._search_barcode(barcode)
        if not product:
            if barcode:
                inventory_vals = {'unknown_line_ids': [[0, False, {
                    'barcode': barcode,
                    'quantity': qty,
                }]]}
                inventory.write(inventory_vals)
                return {'state': 'unknown_barcode_added'}
            else:
                return {'state': 'no_barcode'}

        # Check if there is existing line with the product
        lines = line_obj.search([
            ('inventory_id', '=', inventory.id),
            ('location_id', '=', location_id),
            ('product_id', '=', product.id)])
        if not lines or lines[0].product_qty == 0:
            line_vals = {
                'location_id': location_id,
                'product_id': product.id,
                'product_uom_id': product.uom_id.id,
                'product_qty': qty,
            }
            inventory_vals = {'line_ids': [[0, False, line_vals]]}
            inventory.write(inventory_vals)
            return {'state': 'write_ok'}
        elif len(lines) == 1:
            if mode == 'ask':
                return {'state': 'duplicate', 'qty': lines[0].product_qty}
            elif mode == 'add':
                qty += lines[0].product_qty
            lines[0].write({'product_qty': qty})
            return {'state': 'write_ok'}
        else:
            return {'state': 'many_duplicate_lines'}

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
    def _export_inventory_line(self, line, custom_fields):
        return {
            'id': line.id,
            'product': self._export_product(line.product_id, custom_fields),
            'location': self._export_location(line.location_id),
            'expected_qty': line.theoretical_qty,
        }

    @api.model
    def _export_product(self, product, custom_fields, barcode_qty=0):
        # Custom product fields
        custom_vals = {}
        for field_name, field_display in custom_fields.iteritems():
            if field_name[-3:] == '_id':
                value = getattr(product, field_name).name
            elif field_name[-4:] == '_ids':
                value = ", ".join(
                    [attr.name for attr in getattr(product, field_name)])
            else:
                value = getattr(product, field_name)
            custom_vals[field_display] = value

        return {
            'id': product.id,
            'name': product.name,
            'barcode': product.ean13,
            'barcode_qty': barcode_qty,
            'custom_vals': custom_vals,
        }

    # Custom Section
    @api.model
    def _extract_param(self, params, value_path):
        if not type(params) is dict:
            return False
        if '.' in value_path:
            # Recursive call
            value_path_split = value_path.split('.')
            first_key = value_path_split[0]
            return self._extract_param(
                params.get(first_key),
                '.'.join(value_path_split[1:]))
        else:
            return params.get(value_path, False)

    @api.model
    def _guess_product_qty(self, barcode):
        """Overload Me. Some barcodes contains in the part of it,
        the quantity of the product. directly like Weight Barcode, or
        indirectly like price barcode.
        This function should return a tuple (product, qty) if found, or
        (False, False) otherwise."""
        return (False, False)

    @api.model
    def _get_custom_fields(self):
        """Return a list of (field_name, field_display) for each custom
        product fields that should be displayed during the inventory.

        Don't work yet with computed fields (like display_name)"""

        def _get_field_display(obj, field_name):
            translation_obj = obj.env['ir.translation']
            # Determine model name
            if field_name in obj.env['product.product']._columns:
                model = 'product.product'
            else:
                model = 'product.template'
            # Get translation if defined
            translation_ids = translation_obj.search([
                ('lang', '=', obj.env.context.get('lang', False)),
                ('type', '=', 'field'),
                ('name', '=', '%s,%s' % (model, field_name))])
            if translation_ids:
                return translation_ids[0].value
            else:
                return obj.env[model]._columns[field_name].string

        # Get custom fields
        res = {}

        company = self.env.user.company_id
        custom_field_names = [
            x.name for x in company.mobile_inventory_product_field_ids]

        # Add Custom product fields
        for field_name in custom_field_names:
            res[field_name] = _get_field_display(self, field_name)
        return res

    @api.model
    def _search_barcode(self, barcode):
        product_obj = self.env['product.product']
        products = product_obj.search([('ean13', '=', barcode)])
        barcode_qty = 0
        if not products:
            product, barcode_qty = self._guess_product_qty(barcode)
        else:
            product = products[0]
        if not product:
            return (False, False)
        else:
            return (product, barcode_qty)
