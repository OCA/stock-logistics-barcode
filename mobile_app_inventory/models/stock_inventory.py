# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.osv import fields
from openerp.osv.orm import Model
from openerp.tools.translate import _


class StockInventory(Model):
    _inherit = 'stock.inventory'

    # Compute Section
    def compute_inventory_line_qty(
            self, cr, uid, ids, name, args, context=None):
        res = {}
        for inventory in self.browse(cr, uid, ids, context=context):
            res[inventory.id] = len(inventory.inventory_line_id)
        return res

    # Columns Section
    _columns = {
        'inventory_line_qty': fields.function(
            compute_inventory_line_qty, string='Lines Qty', type='integer'),
        'scan_ok': fields.boolean(string='Scan Finished'),
    }

    def create_by_scan(
            self, cr, uid, name, context=None):
        vals = self.default_get(
            cr, uid, self._defaults.keys(), context=context)
        vals.update({'name': _('%s (Barcode Reader)') % (name)})
        return super(StockInventory, self).create(
            cr, uid, vals, context=context)

    def add_inventory_line_by_scan(
            self, cr, uid, id, location_id, product_id, qty, mode,
            context=None):
        """
        Add a new line in the current inventory
        @param id: the inventory id;
        @param location_id, product_id ;
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
        qty = float(qty)
        product_obj = self.pool['product.product']
        line_obj = self.pool['stock.inventory.line']
        product = product_obj.browse(cr, uid, product_id, context=context)

        # Check if there is existing line with the product
        line_ids = line_obj.search(cr, uid, [
            ('inventory_id', '=', id),
            ('location_id', '=', location_id),
            ('product_id', '=', product_id)], context=context)
        if not line_ids:
            line_vals = {
                'location_id': location_id,
                'product_id': product_id,
                'product_uom': product.uom_id.id,
                'product_qty': qty,
            }
            inventory_vals = {'inventory_line_id': [[0, False, line_vals]]}
            self.write(cr, uid, [id], inventory_vals, context=context)
            return {'state': 'write_ok'}
        elif len(line_ids) == 1:
            line = line_obj.browse(cr, uid, line_ids[0], context=context)
            if mode == 'ask':
                return {'state': 'duplicate', 'qty': line.product_qty}
            elif mode == 'add':
                qty += line.product_qty
            line_obj.write(
                cr, uid, line_ids[0], {'product_qty': qty}, context=context)
            return {'state': 'write_ok'}
        else:
            return {'state': 'many_duplicate_lines'}
