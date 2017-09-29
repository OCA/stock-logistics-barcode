# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.osv import fields
from openerp.osv.orm import Model
from openerp.tools.translate import _
from openerp import api

class StockInventory(Model):
    _inherit = 'stock.inventory'

    @api.multi
    def compute_inventory_line_qty(self, ids):
        import pdb
        res = {}
        for inventory in self:
            res[inventory.id] = len(inventory.line_ids)
        return res
            # Compute Section
    #def compute_inventory_line_qty(
    #        self, cr, uid, ids, name, args, context=None):
    #    res = {}
    #    for inventory in self.browse(cr, uid, ids, context=context):
    #        import pdb
    #        pdb.set_trace()
    #        res[inventory.id] = len(inventory.inventory_line_id)
    #    return res

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

    @api.multi
    def add_inventory_line_by_scan(
            self, location_id, product_id, qty, mode,
            ):
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

        silo = self.env['stock.inventory.line']
        inventory_id = self.id
        product = self.env['product.product'].browse(product_id)
        ilines = silo.search([
            ('inventory_id', '=', inventory_id),
            ('product_id', '=', product.id),
            ])
        if len(ilines) == 1:
            ilines[0].product_qty = qty
        elif len(ilines) > 1:
            return {'warning': {
                'title': _('Error'),
                'message': _(
                    'Several inventory lines exists for this product. '
                    'This scenario is not supported for the moment. '
                    'It may be caused by the fact that you have '
                    'sub-locations in the stock location of this '
                    'inventory and this product is present in '
                    'several sub-locations, or by the fact that you '
                    'track Serial Numbers for this product.')}}
        else:
            new_iline = silo.create({
                'inventory_id': inventory_id,
                'location_id': self.location_id.id,
                'product_id': product.id,
                'product_uom_id': product.uom_id.id,
                'product_qty': qty,
                })
            self.inventory_line_id = new_iline
        return {'state': 'write_ok'}


        qty = float(qty)
        product_obj = self.env['product.product']
        line_obj = self.env['stock.inventory.line']
        product = product_obj.browse(product_id)


        # Check if there is existing line with the product
        line_ids = line_obj.search([
            ('inventory_id', '=', self.id),
            ('location_id', '=', location_id),
            ('product_id', '=', product_id)])
        if not line_ids:
            line_vals = {
                'location_id': location_id,
                'product_id': product_id,
                'product_uom': product.uom_id.id,
                'product_qty': qty,
            }
            inventory_vals = {'inventory_line_id': [[0, False, line_vals]]}
            self.write(inventory_vals)
            return {'state': 'write_ok'}
        elif len(line_ids) == 1:
            line = line_obj.browse(line_ids[0])
            if mode == 'ask':
                return {'state': 'duplicate', 'qty': line.product_qty}
            elif mode == 'add':
                qty += line.product_qty
            line_obj.write(
                 line_ids[0], {'product_qty': qty})
            return {'state': 'write_ok'}
        else:
            return {'state': 'many_duplicate_lines'}
