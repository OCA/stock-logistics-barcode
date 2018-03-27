# -*- coding: utf-8 -*-
# Copyright 2018 Simone Rubino - Agile Business Group
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models, _


class StockPicking(models.Model):
    _name = 'stock.picking'
    _inherit = ['stock.picking', 'barcodes.barcode_events_mixin']

    def on_barcode_scanned(self, barcode):
        res = super(StockPicking, self).on_barcode_scanned(barcode)
        if res:
            # Parents haven't found any correspondence, let's do our own search
            return self._check_lot(barcode)
        return res

    def _check_lot(self, barcode):
        lot_id = self.env['stock.production.lot'].search([
            ('name', '=', barcode)
        ], limit=1)
        if not lot_id:
            return {
                'warning': {
                    'title': _('No lot found'),
                    'message': (_('There is no production lot '
                                'corresponding to "%(barcode)s"')
                                % {'barcode': barcode})
                    }}

        product = lot_id.product_id
        corresponding_po = self.pack_operation_product_ids.filtered(
            lambda r:
            r.product_id.id == product.id and
            not r.result_package_id and
            not r.location_processed)
        if corresponding_po:
            corresponding_po = corresponding_po[0]
            corresponding_po.on_barcode_scanned(barcode)
            new_pl = corresponding_po.pack_lot_ids[0]
            if new_pl:
                corresponding_po.write({
                    'pack_lot_ids': [(0, 0, {
                        'qty': new_pl.qty,
                        'lot_id': new_pl.lot_id.id,
                        'plus_visible': new_pl.plus_visible})]})
            po_values = corresponding_po.read()[0]
            # Trigger onchange methods, but
            # exclude _barcode_scanned to avoid recursion
            po_values.pop('_barcode_scanned')
            po_changed_values = corresponding_po.onchange(
                po_values,
                po_values.keys(),
                dict.fromkeys(po_values.keys(), str(1))
            ).get('value')
            if po_changed_values:
                corresponding_po.write(po_changed_values)
            corresponding_po.save()
            # Can't return anything but None because this will be
            # evaluated as an onchange method
            return
        return {'warning': {
            'title': _('Wrong barcode'),
            'message': _('Pack operation for product %s does not exist')
                % product.name_get()[0][1]}}
