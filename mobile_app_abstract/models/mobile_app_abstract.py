# Copyright (C) 2019 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class MobileAppAbstract(models.AbstractModel):
    _name = 'mobile.app.mxin'

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
