# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, models


class ProductProduct(models.Model):
    _inherit = 'product.product'

    _MOBILE_INVENTORY_MANDATORY_FIELDS = ['id', 'name', 'ean13']

    # API Section
    @api.model
    def mobile_inventory_load_products(self, inventory_id):
        """API that will return a dictionnary for each products.
        {'ean1': vals1, 'ean2': vals2}
        If inventory_id is set, the products will be the products in
        the inventory lines of the given inventory.
        If not, all products with barcodes will be returned.
        """
        inventory_obj = self.env['stock.inventory']
        if not inventory_id:
            products = self.search([('ean13', '!=', False)])
        else:
            inventory = inventory_obj.browse(inventory_id)
            products = inventory.mapped('line_ids.product_id')
        return products._mobile_inventory_load_product()

    @api.model
    def mobile_inventory_load_product(self, barcode):
        """API that will return the same dictionnary as
        mobile_inventory_load_product but for one product (given a barcode)
        the extra feature of this function, is to have the possibility
        to return a product that has a different EAN13 than the parameter
        This function is usefull for Priced / Weighted barcode.
        If that case, an extra key 'barcode_qty' will be returned too."""
        # Try to search exact product with the given barcode
        product = self.search([('ean13', '=', barcode)])
        qty = 0
        if not product:
            product, qty = self._mobile_inventory_guess_product_qty(barcode)
        if not product:
            return False
        res = product[0]._mobile_inventory_load_product()
        res[0]['barcode_qty'] = qty
        return res

    # Private Section
    @api.model
    def _mobile_inventory_guess_product_qty(self, barcode):
        """Overload Me. Some barcodes contains in the part of it,
        the quantity of the product. directly like Weight Barcode, or
        indirectly like price barcode.
        This function should return a tuple (product, qty) if found, or
        False otherwise."""
        return False

    @api.multi
    def _mobile_inventory_load_product(self):

        def _get_field_name(product_obj, field):
            translation_obj = product_obj.env['ir.translation']
            # Determine model name
            if field in product_obj.env['product.product']._columns:
                model = 'product.product'
            else:
                model = 'product.template'
            # Get translation if defined
            translation_ids = translation_obj.search([
                ('lang', '=', product_obj.env.context.get('lang', False)),
                ('type', '=', 'field'),
                ('name', '=', '%s,%s' % (model, field))])
            if translation_ids:
                return translation_ids[0].value
            else:
                return product_obj.env[model]._columns[field].string

        res = {}
        # Get custom fields
        company = self.env.user.company_id
        mobile_inventory_custom_fields = [
            x.name for x in company.mobile_inventory_product_field_ids]

        for product in self:
            res[product.ean13] = {}
            # Add Mandatory product fields
            for field in self._MOBILE_INVENTORY_MANDATORY_FIELDS:
                res[product.ean13][field] = getattr(product, field)

            # Add Custom product fields
            for field in mobile_inventory_custom_fields:
                field_name = _get_field_name(self, field)
                if field[-3:] == '_id':
                    value = getattr(product, field).name
                else:
                    value = getattr(product, field)
                res[product.ean13][field] = {
                    'value': value,
                    'field_name': field_name,
                }
        return res
