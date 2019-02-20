# Copyright (C) 2019 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, models
from odoo.tools.float_utils import float_is_zero


class MobileAppPicking(models.Model):
    _name = 'mobile.app.picking'
    _inherit = ['mobile.app.mxin']

    # Overload Section
    @api.model
    def get_custom_fields_list(self):
        picking_id = self.env.context.get('picking_id', False)
        StockPicking = self.env['stock.picking']
        if picking_id:
            picking = StockPicking.browse(picking_id)
            return [
                x.name
                for x in picking.picking_type_id.mobile_product_field_ids]

    @api.model
    def get_picking_types(self):
        """Return Picking Types available for the Mobile App
        :return: [picking_type_1_vals, picking_type_2_vals, ...]
        .. seealso:: _export_picking_type() for picking type vals details.
        """
        StockPickingType = self.env['stock.picking.type']
        picking_types = StockPickingType.search(
            self._get_picking_type_domain())
        return [
            self._export_picking_type(picking_type)
            for picking_type in picking_types]

    @api.model
    def get_pickings(self, params):
        """ Return pickings of a given picking type
        :param params: {'picking_type': picking_type_1_vals}
        :return: [picking_1_vals, picking_2_vals, ...]
        .. seealso::
            _export_picking_type() for picking type vals details
            _export_picking() for picking vals details
        """
        StockPicking = self.env['stock.picking']
        picking_type_id = self._extract_param(params, 'picking_type.id')
        pickings = StockPicking.search(
            self._get_picking_domain(picking_type_id))
        return [
            self._export_picking(picking) for picking in pickings]

    @api.model
    def get_move_lines(self, params):
        """ Return move lines of a given picking.
        :param params: {'picking': picking_vals}
        :return: [move_line_1_vals, move_line_2_vals, ...]
        .. seealso::
            _export_picking() for picking vals details
            _export_move_line() for move line vals details
        """
        StockMoveLine = self.env['stock.move.line']
        picking_id = self._extract_param(params, 'picking.id')
        lines = StockMoveLine.search([('picking_id', '=', picking_id)])
        custom_fields = self.with_context(
            picking_id=picking_id)._get_custom_fields_dict()
        return [
            self._export_move_line(line, custom_fields)
            for line in lines]

    @api.model
    def set_quantity(self, params):
        """ Return move lines of a given picking.
        :param params: {'move_line': move_line_vals, 'quantity': integer}
        """
        StockMoveLine = self.env['stock.move.line']
        move_line_id = self._extract_param(params, 'move_line.id')
        qty_done = self._extract_param(params, 'qty_done', 0)
        move_line = StockMoveLine.search([('id', '=', move_line_id)])
        if move_line:
            move_line.qty_done = qty_done
        return True

    @api.model
    def confirm_picking(self, params):
        """ Confirm a given picking
        :param params: {'picking': picking_vals}
        """
        StockPicking = self.env['stock.picking']
        WizardBackorder = self.env['stock.backorder.confirmation']
        WizardImmediate = self.env['stock.immediate.transfer']
        DecimalPrecision = self.env['decimal.precision']

        picking_id = self._extract_param(params, 'picking.id')
        precision_digits = DecimalPrecision.precision_get(
            'Product Unit of Measure')

        picking = StockPicking.search([('id', '=', picking_id)])
        no_quantities_done = all(float_is_zero(
            move_line.qty_done, precision_digits=precision_digits)
            for move_line in picking.move_line_ids)

        if no_quantities_done:
            wizard = WizardImmediate.create(
                {'pick_ids': [(6, 0, picking.ids)]})
            wizard.process()
        else:
            wizard = WizardBackorder.create(
                {'pick_ids': [(6, 0, picking.ids)]})
            if picking.picking_type_id.mobile_backorder_create:
                wizard.process()
            else:
                wizard.process_cancel_backorder()
        return True

    # Domain Section
    @api.model
    def _get_picking_type_domain(self):
        return [('mobile_available', '=', True)]

    @api.model
    def _get_picking_domain(self, picking_type_id=False):
        return [
            ('state', '=', 'assigned'),
            ('picking_type_id', '=', picking_type_id),
        ]

    # Export Section
    @api.model
    def _export_picking_type(self, picking_type):
        return {
            'id': picking_type.id,
            'name': picking_type.name,
            'warehouse': self._export_warehouse(picking_type.warehouse_id),
            'code': picking_type.code,
        }

    @api.model
    def _export_warehouse(self, warehouse):
        return {
            'id': warehouse.id,
            'code': warehouse.code,
            'name': warehouse.name,
        }

    @api.model
    def _export_picking(self, picking):
        if not picking:
            return {}
        return {
            'id': picking.id,
            'name': picking.name,
            'state': picking.state,
            'backorder': self._export_picking(picking.backorder_id),
            'partner': self._export_partner(picking.partner_id),
        }

    @api.model
    def _export_move_line(self, line, custom_fields):
        return {
            'id': line.id,
            'uom': self._export_uom(line.product_uom_id),
            'product': self._export_product(line.product_id, custom_fields),
            'qty_done': line.qty_done,
            'qty_expected': line.product_uom_qty,
        }
