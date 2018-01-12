# -*- coding: utf-8 -*-
# © 2015-2018 Akretion (http://www.akretion.com)
# @author Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import api, fields, models, _
import odoo.addons.decimal_precision as dp
from odoo.exceptions import UserError
from odoo.tools import float_compare, float_is_zero


class StockInventoryBarcode(models.TransientModel):
    _name = 'stock.inventory.barcode'
    _description = 'Stock Inventory Barcode Wizard'

    product_code = fields.Char(
        string='Barcode or Internal Reference',
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
                ('barcode', '=', self.product_code),
                ('default_code', '=ilike', self.product_code)])
            if len(products) == 1:
                self.product_id = products[0]
            elif len(products) > 1:
                return {'warning': {
                    'title': _('Error'),
                    'message': _(
                        'Several products have been found '
                        'with this code as Barcode or Internal Reference:\n %s'
                        '\nYou should select the right product manually.'
                        ) % '\n'.join([
                            product.display_name for product in products
                            ])}}
            else:
                return {'warning': {
                    'title': _('Error'),
                    'message': _(
                        'No product found with this code as '
                        'Barcode nor Internal Reference. You should select '
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

    def save(self):
        self.ensure_one()
        if not self.inventory_line_id:
            raise UserError(_('No related inventory line'))
        prec = self.env['decimal.precision'].precision_get(
            'Product Unit of Measure')
        if not float_is_zero(self.add_qty, precision_digits=prec):
            self.inventory_line_id.product_qty += self.add_qty
        elif float_compare(
                self.change_qty, self.product_qty, precision_digits=prec):
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
