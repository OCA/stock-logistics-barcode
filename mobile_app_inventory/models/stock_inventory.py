# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import _, api, fields, models


class StockInventory(models.Model):
    _inherit = 'stock.inventory'

    # Columns Section
#    inventory_line_qty = fields.Integer(
#        compute='_compute_inventory_line_qty', string='Lines Qty', store=True)

    mobile_available = fields.Boolean(
        string='Available on Mobile', default=True,
        help="Check this box if you want that a user making an inventory"
        " by the Mobile App can work on this inventory.")

#    @api.depends('line_ids')
#    def _compute_inventory_line_qty(self):
#        for inventory in self:
#            inventory.inventory_line_qty = len(inventory.line_ids)

#    @api.model
#    def mobile_create(self, name):
#        vals = self.default_get(self._defaults.keys())
#        vals.update({
#            'name': _('%s (Mobile App)') % (name),
#            'filter': 'partial',
#        })
#        inventory = super(StockInventory, self).create(vals)
#        inventory.prepare_inventory()
#        res = {'inventory_line_qty': 0}
#        for field in ['id', 'name', 'date']:
#            res[field] = getattr(inventory, field)
#        return res

#    @api.multi
#    def mobile_add_inventory_line(self, location_id, product_id, qty, mode):
#        """
#        Add a new line in the current inventory
#        @param location_id, product_id ;
#        @qty : the quantity to set or to add depending of the mode;
#        @mode :
#            'ask': Do nothing if there is a duplicate line;
#            'add': Add quantity to the duplicate line;
#            'replace': Replace quantity of the duplicate line;
#        return:
#            {'state': 'write_ok'}:
#                Update / creation OK
#            {'state': 'many_duplicate_lines'}:
#                Too many duplicate lines. not possible to process
#            {'state': 'duplicate', qty: xxx}:
#                There is a duplicate. Qty is the current quantity
#        """
#        self.ensure_one()
#        qty = float(qty)
#        product_obj = self.env['product.product']
#        line_obj = self.env['stock.inventory.line']
#        product = product_obj.browse(product_id)

#        # Check if there is existing line with the product
#        lines = line_obj.search([
#            ('inventory_id', '=', self.id),
#            ('location_id', '=', location_id),
#            ('product_id', '=', product_id)])
#        if not lines:
#            line_vals = {
#                'location_id': location_id,
#                'product_id': product_id,
#                'product_uom_id': product.uom_id.id,
#                'product_qty': qty,
#            }
#            inventory_vals = {'line_ids': [[0, False, line_vals]]}
#            self.write(inventory_vals)
#            return {'state': 'write_ok'}
#        elif len(lines) == 1:
#            if mode == 'ask':
#                return {'state': 'duplicate', 'qty': lines[0].product_qty}
#            elif mode == 'add':
#                qty += lines[0].product_qty
#            lines[0].write({'product_qty': qty})
#            return {'state': 'write_ok'}
#        else:
#            return {'state': 'many_duplicate_lines'}

        # Current Raphael Code to check.
        # Pas compris
#        silo = self.env['stock.inventory.line']
#        inventory_id = self.id
#        product = self.env['product.product'].browse(product_id)
#        ilines = silo.search([
#            ('inventory_id', '=', inventory_id),
#            ('product_id', '=', product.id),
#            ])
#        if len(ilines) == 1:
#            ilines[0].product_qty = qty
#        elif len(ilines) > 1:
#            return {'warning': {
#                'title': _('Error'),
#                'message': _(
#                    'Several inventory lines exists for this product. '
#                    'This scenario is not supported for the moment. '
#                    'It may be caused by the fact that you have '
#                    'sub-locations in the stock location of this '
#                    'inventory and this product is present in '
#                    'several sub-locations, or by the fact that you '
#                    'track Serial Numbers for this product.')}}
#        else:
#            new_iline = silo.create({
#                'inventory_id': inventory_id,
#                'location_id': self.location_id.id,
#                'product_id': product.id,
#                'product_uom_id': product.uom_id.id,
#                'product_qty': qty,
#                })
#            self.inventory_line_id = new_iline
#        return {'state': 'write_ok'}
