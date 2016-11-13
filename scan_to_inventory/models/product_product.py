# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.osv.orm import Model


class ProductProduct(Model):
    _inherit = 'product.product'

    _SCAN_TO_INVENTORY_MANDATORY_FIELDS = ['id', 'name', 'ean13']

    def _scan_to_inventory_product_field_ids(self, cr, uid, context=None):
        user_obj = self.pool['res.users']
        company = user_obj.browse(cr, uid, uid, context=context).company_id
        return [x.name for x in company.scan_inventory_product_field_ids]

    def scan_to_inventory_load_product(self, cr, uid, context=None):
        def _get_field_name(pool, cr, uid, field, model=False):
            translation_obj = self.pool['ir.translation']
            # Determine model name
            if not model:
                if field in pool.pool['product.product']._columns:
                    model = 'product.product'
                else:
                    model = 'product.template'
            # Get translation if defined
            translation_ids = translation_obj.search(cr, uid, [
                ('lang', '=', context.get('lang', False)),
                ('type', '=', 'field'),
                ('name', '=', '%s,%s' % (model, field))],
                context=context)
            if translation_ids:
                return translation_obj.browse(
                    cr, uid, translation_ids[0], context=context).value
            else:
                return pool.pool[model]._columns[field].string

        context = context and context or {}
        product_fields = self._scan_to_inventory_product_field_ids(
            cr, uid, context=context)

        res = {}
        product_ids = self.search(
            cr, uid, [('ean13', '!=', False)], context=context)
        products = self.browse(cr, uid, product_ids, context=context)
        for product in products:
            res[product.ean13] = {}
            # Add product fields
            for field in self._SCAN_TO_INVENTORY_MANDATORY_FIELDS:
                res[product.ean13][field] = getattr(product, field)

            for field in product_fields:
                if field[-3:] == '_id':
                    res[product.ean13][field] = {
                        'id': getattr(product, field).id,
                        'value': getattr(product, field).name,
                        'field_name': _get_field_name(self, cr, uid, field),
                    }
                else:
                    res[product.ean13][field] = {
                        'value': getattr(product, field),
                        'field_name': _get_field_name(self, cr, uid, field),
                    }
        return res
