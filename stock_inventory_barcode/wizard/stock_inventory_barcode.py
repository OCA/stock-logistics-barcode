# -*- coding: utf-8 -*-
##############################################################################
#
#    Stock Inventory Barcode module for Odoo
#    Copyright (C) 2015 Akretion (http://www.akretion.com)
#    @author Alexis de Lattre <alexis.delattre@akretion.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, fields, api, _
import openerp.addons.decimal_precision as dp
from openerp.exceptions import Warning as UserError


class StockInventoryBarcode(models.TransientModel):
    _name = 'stock.inventory.barcode'
    _description = 'Stock Inventory Barcode Wizard'

    product_code = fields.Char(
        string='EAN13 or Internal Reference',
        help="This field is designed to be filled with a barcode reader")
    product_id = fields.Many2one(
        'product.product', string='Product', required=True)
    theoretical_qty = fields.Float(
        related='inventory_line_id.theoretical_qty', readonly=True)
    product_qty = fields.Float(
        string='Current Real Quantity',
        related='inventory_line_id.product_qty', readonly=True)
    change_qty = fields.Float(
        string='Change Real Quantity',
        digits=dp.get_precision('Product Unit of Measure'))
    add_qty = fields.Float(
        string='Add to Real Quantity',
        digits=dp.get_precision('Product Unit of Measure'))
    inventory_line_id = fields.Many2one(
        'stock.inventory.line', string='Stock Inventory Line')

    @api.onchange('product_code')
    def product_code_change(self):
        if self.product_code:
            products = self.env['product.product'].search([
                '|',
                ('ean13', '=', self.product_code),
                ('default_code', '=ilike', self.product_code)])
            if len(products) == 1:
                self.product_id = products[0]
            elif len(products) > 1:
                return {'warning': {
                    'title': _('Error'),
                    'message': _(
                        'Several products have been found '
                        'with this code as EAN13 or Internal Reference:\n %s'
                        '\nYou should select the right product manually.'
                        ) % '\n'.join([
                            product.name_get()[0][1] for product in products
                            ])}}
            else:
                return {'warning': {
                    'title': _('Error'),
                    'message': _(
                        'No product found with this code as '
                        'EAN13 nor Internal Reference. You should select '
                        'the right product manually.')}}

    @api.onchange('product_id')
    def product_id_change(self):
        assert self._context['active_model'] == 'stock.inventory',\
            'wrong underlying model'
        assert self._context['active_id'], 'Missing active_id in ctx'
        if self.product_id:
            silo = self.env['stock.inventory.line']
            sio = self.env['stock.inventory']
            inventory_id = self._context['active_id']
            ilines = silo.search([
                ('inventory_id', '=', inventory_id),
                ('product_id', '=', self.product_id.id),
                ])
            if len(ilines) == 1:
                self.inventory_line_id = ilines[0]
                self.change_qty = ilines[0].product_qty
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
                inventory = sio.browse(inventory_id)
                new_iline = silo.create({
                    'inventory_id': inventory_id,
                    'location_id': inventory.location_id.id,
                    'product_id': self.product_id.id,
                    'product_uom_id': self.product_id.uom_id.id,
                    })
                self.inventory_line_id = new_iline

    @api.multi
    def save(self):
        self.ensure_one()
        if not self.inventory_line_id:
            raise UserError(_('No related inventory line'))
        if self.add_qty:
            self.inventory_line_id.product_qty += self.add_qty
        elif self.change_qty != self.product_qty:
            self.inventory_line_id.product_qty = self.change_qty
        action = {
            'name': _('Stock Inventory Barcode Wizard'),
            'type': 'ir.actions.act_window',
            'res_model': 'stock.inventory.barcode',
            'view_mode': 'form',
            'nodestroy': True,
            'target': 'new',
            'context': self._context,
            }
        return action
