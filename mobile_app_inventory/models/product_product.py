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
    def mobile_inventory_load_product(self, barcode):
        # Try to search exact product with the given barcode
        product = self.search([('ean13', '=', barcode)])
        qty = 0
        if not product:
            product, qty = self._mobile_inventory_guess_product_qty(barcode)
        if not product:
            return False
        res = product[0]._mobile_inventory_load_product()
        if qty:
            res[0]['barcode_qty'] = qty
        return res


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
        # def _get_field_name(pool, cr, uid, field, model=False):
        #    translation_obj = self.pool['ir.translation']
        #    # Determine model name
        #    if not model:
        #        if field in pool.pool['product.product']._columns:
        #            model = 'product.product'
        #        else:
        #            model = 'product.template'
        #    # Get translation if defined
        #    translation_ids = translation_obj.search(cr, uid, [
        #        ('lang', '=', context.get('lang', False)),
        #        ('type', '=', 'field'),
        #        ('name', '=', '%s,%s' % (model, field))],
        #        context=context)
        #    if translation_ids:
        #        return translation_obj.browse(
        #            cr, uid, translation_ids[0], context=context).value
        #    else:
        #        return pool.pool[model]._columns[field].string

        res = {}

        # Get custom fields
        company = self.env.user.company_id
        mobile_inventory_custom_fields = [
            x.name for x in company.mobile_inventory_product_field_ids]

        for product in products:
            res[product.ean13] = {}
            # Add Mandatory product fields
            for field in self._MOBILE_INVENTORY_MANDATORY_FIELDS:
                res[product.ean13][field] = getattr(product, field)

            # Add Custom product fields
            for field in mobile_inventory_custom_fields:
                if field[-3:] == '_id':
                    res[product.ean13][field] = {
                        'id': getattr(product, field).id,
                        'value': getattr(product, field).name,
                        'field_name': "FIXME"
                        # _get_field_name(self, cr, uid, field),
                    }
                else:
                    res[product.ean13][field] = {
                        'value': getattr(product, field),
                        'field_name': "FIXME"
                        # _get_field_name(self, cr, uid, field),
                    }
        print res
        return res
