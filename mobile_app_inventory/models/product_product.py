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
    def mobile_inventory_load_product(self, inventory_id):
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
        # TODO Add location in args
        print ">>>>>>>>>>>>>>>>>>>>>>>>>>>>"
        products = self.search([('ean13', '!=', False)])
        print products

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
