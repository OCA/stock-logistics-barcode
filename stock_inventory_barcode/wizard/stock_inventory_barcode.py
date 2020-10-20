# Copyright 2015-2020 Akretion (http://www.akretion.com)
# @author Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import api, fields, models, _
import odoo.addons.decimal_precision as dp
from odoo.exceptions import UserError
from odoo.tools import float_compare, float_is_zero


class StockInventoryBarcode(models.TransientModel):
    _name = 'stock.inventory.barcode'
    _description = 'Stock Inventory Barcode Wizard'

    inventory_id = fields.Many2one(
        'stock.inventory', string='Inventory', required=True)
    inventory_location_id = fields.Many2one(
        'stock.location', required=True, string='Root Inventory Location')
    product_code = fields.Char(
        string='Barcode or Internal Reference',
        help="This field is designed to be filled with a barcode reader")
    product_id = fields.Many2one(
        'product.product', string='Product', required=True,
        domain=[('type', '=', 'product')])
    uom_id = fields.Many2one(
        'uom.uom', string='Unit of measure', required=True)
    uom_name = fields.Char(related='uom_id.name')
    location_id = fields.Many2one(
        'stock.location', string='Location', required=True)
    multi_stock_location = fields.Boolean(readonly=True)
    lot_id = fields.Many2one(
        'stock.production.lot', string='Lot')
    product_tracking = fields.Selection([
        ('serial', 'By Unique Serial Number'),
        ('lot', 'By Lots'),
        ('none', 'No Tracking'),
        ], string="Tracking", required=True)
    note = fields.Text()
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

    @api.model
    def default_get(self, fields_list):
        res = super(StockInventoryBarcode, self).default_get(fields_list)
        assert self._context.get('active_model') == 'stock.inventory'
        inv = self.env['stock.inventory'].browse(self._context.get('active_id'))
        if inv.state != 'confirm':
            raise UserError(_(
                "You cannot start the barcode interface on inventory '%s' "
                "which is not 'In Progress'.") % inv.display_name)
        res['inventory_id'] = inv.id
        root_loc = inv.location_id
        res['inventory_location_id'] = root_loc.id
        if root_loc.child_ids:
            res['multi_stock_location'] = True
        else:
            res['multi_stock_location'] = False
            res['location_id'] = root_loc.id
        return res

    @api.onchange('product_code')
    def product_code_change(self):
        if self.product_code:
            products = self.env['product.product'].search([
                '|',
                ('barcode', '=', self.product_code),
                ('default_code', '=ilike', self.product_code),
                ('type', '=', 'product'),
                ])
            if len(products) == 1:
                product = products[0]
                self.product_id = product
                self.product_tracking = product.tracking
                self.uom_id = product.uom_id
            elif len(products) > 1:
                return {'warning': {
                    'title': _('Error'),
                    'message': _(
                        'Several stockable products have been found '
                        'with this code as Barcode or Internal Reference:\n %s'
                        '\nYou should select the right product manually.'
                        ) % '\n'.join([
                            product.display_name for product in products
                            ])}}
            else:
                return {'warning': {
                    'title': _('Error'),
                    'message': _(
                        'No stockable product found with this code as '
                        'Barcode nor Internal Reference. You should select '
                        'the right product manually.')}}

    @api.onchange('product_id')
    def product_id_change(self):
        if self.product_id:
            self.product_tracking = self.product_id.tracking
            self.uom_id = self.product_id.uom_id
            if not self.product_tracking or self.product_tracking == 'none':
                self.lot_id = False
        else:
            self.product_tracking = False
            self.uom_id = False
            self.lot_id = False
            self.note = False

    @api.onchange('product_id', 'location_id', 'lot_id', 'uom_id')
    def product_lot_loc_change(self):
        res = {'warning': {}}
        if self.product_id and self.location_id and self.uom_id:
            if self.uom_id != self.product_id.uom_id:
                self.uom_id = self.product_id.uom_id
                res['warning'] = {
                    'title': _('Error'),
                    'message': _(
                        "You cannot change the unit of measure of the "
                        "product: it is been restored to '%s'.")
                    % self.product_id.uom_id.name}
            if not self.product_id.tracking or self.product_id.tracking == 'none':
                if self.lot_id:
                    raise UserError(_(
                        "Product '%s' is not tracked by lot/serial so the "
                        "lot field must be empty. This should never "
                        "happen.") % self.product_id.display_name)
                self.update_wiz_screen(res)
            elif self.lot_id:
                self.update_wiz_screen(res)
        return res

    def update_wiz_screen(self, res):
        silo = self.env['stock.inventory.line']
        ilines = silo.search([
            ('inventory_id', '=', self.inventory_id.id),
            ('product_id', '=', self.product_id.id),
            ('location_id', '=', self.location_id.id),
            ('prod_lot_id', '=', self.lot_id and self.lot_id.id or False),
            ])
        if len(ilines) == 1:
            self.inventory_line_id = ilines[0]
            self.change_qty = ilines[0].product_qty
        elif len(ilines) > 1:
            res['warning'] = {
                'title': _('Error'),
                'message': _(
                    'Several inventory lines exists for this product '
                    '(and lot) on the same stock location. '
                    'This should happen only when using packaging, '
                    'but this scenario is not supported for the moment.')}
        else:
            new_iline = silo.create({
                'inventory_id': self.inventory_id.id,
                'product_id': self.product_id.id,
                'prod_lot_id': self.lot_id and self.lot_id.id or False,
                'product_uom_id': self.uom_id.id,
                'location_id': self.location_id.id,
                })
            self.inventory_line_id = new_iline
        domain_same_product = [
            ('inventory_id', '=', self.inventory_id.id),
            ('product_id', '=', self.product_id.id),
            ('product_qty', '>', 0),
            ]
        if ilines:
            domain_same_product += [('id', 'not in', ilines.ids)]
        same_product_lines = silo.search(domain_same_product)
        note_list = []
        tracking = self.product_id.tracking in ('lot', 'serial') and True or False
        uom_name = self.uom_id.name
        for il in same_product_lines:
            if tracking:
                note_list.append(_(
                    "Lot %s already inventoried on %s with real qty %.3f %s") % (
                        il.prod_lot_id and il.prod_lot_id.display_name or _('<none>'),
                        il.location_id.display_name,
                        il.product_qty,
                        uom_name))
            else:
                note_list.append(_(
                    "Already inventoried on %s with real qty %.3f %s") % (
                        il.location_id.display_name,
                        il.product_qty,
                        uom_name))
        if note_list:
            note = '\n'.join(note_list)
            self.note = note
        else:
            self.note = False

    def save(self):
        self.ensure_one()
        if not self.inventory_line_id:
            raise UserError(_('No related inventory line'))
        if self.inventory_id.state != 'confirm':
            raise UserError(_(
                "The inventory '%s' is not 'In Progress' any more.")
                % self.inventory_id.display_name)
        if self.uom_id != self.product_id.uom_id:
            raise UserError(_(
                "You cannot change the unit of measure. You must "
                "restore the unit of measure of the product (%s).")
                % self.product_id.uom_id.display_name)
        prec = self.env['decimal.precision'].precision_get(
            'Product Unit of Measure')
        if not float_is_zero(self.add_qty, precision_digits=prec):
            prev_inv_line_qty = self.inventory_line_id.product_qty
            self.inventory_line_id.write({
                'product_qty': self.add_qty + prev_inv_line_qty})
        elif float_compare(
                self.change_qty, self.product_qty, precision_digits=prec):
            self.inventory_line_id.write({'product_qty': self.change_qty})
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
