# Copyright (C) 2019 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class MobileAppAbstract(models.AbstractModel):
    _name = 'mobile.app.mxin'

    # To Overload Section
    @api.model
    def get_custom_fields_list(self):
        """Overload this function to define which field values should
        be displayed on the mobile application, when scanning a product"""
        return []

    # Public API Section
    @api.model
    def check_group(self, group_ext_id):
        return self.env.user.has_group(group_ext_id)

    # Export Section
    @api.model
    def _export_partner(self, partner):
        if not partner:
            return {}
        return {
            'id': partner.id,
            'name': partner.name,
            'customer': partner.customer,
            'supplier': partner.supplier,
            'parent_id': self._export_partner(partner.parent_id),
        }

    @api.model
    def _export_uom(self, uom):
        if not uom:
            return {}
        return {
            'id': uom.id,
            'name': uom.name,
        }

    @api.model
    def _export_product(self, product, custom_fields):
        if not product:
            return {}
        # Custom product fields
        custom_vals = {}
        for field_name, field_display in custom_fields.items():
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
            'barcode': product.barcode,
            'custom_vals': custom_vals,
        }

    # Custom Section
    @api.model
    def _extract_param(self, params, value_path, default_value=False):
        if not type(params) is dict:
            return False
        if '.' in value_path:
            # Recursive call
            value_path_split = value_path.split('.')
            first_key = value_path_split[0]
            return self._extract_param(
                params.get(first_key),
                '.'.join(value_path_split[1:]),
                default_value)
        else:
            return params.get(value_path, default_value)

    @api.model
    def _get_custom_fields_dict(self):
        """Return a list of (field_name, field_display) for each custom
        product fields that should be displayed during the inventory.

        Don't work yet with computed fields (like display_name)"""

        # Get custom fields
        res = {}

        custom_field_names = self.get_custom_fields_list()

        # Add Custom product fields
        for field_name in custom_field_names:
            res[field_name] = self._get_field_display(field_name)
        return res

    @api.model
    def _get_field_display(self, field_name):
        IrTranslation = self.env['ir.translation']
        # Determine model name
        if field_name in self.env['product.product']._fields.keys():
            model = 'product.product'
        else:
            model = 'product.template'
        # Get translation if defined
        translation_ids = IrTranslation.search([
            ('lang', '=', self.env.context.get('lang', False)),
            ('type', '=', 'field'),
            ('name', '=', '%s,%s' % (model, field_name))])
        if translation_ids:
            return translation_ids[0].value
        else:
            return self.env[model]._fields[field_name].string
