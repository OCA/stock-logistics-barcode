# Copyright (C) 2019 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import _, api, models
from odoo.exceptions import UserError


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
    def get_moves(self, params):
        """ Return moves of a given picking.
        :param params: {'picking': picking_vals}
        :return: [move_1_vals, move_2_vals, ...]
        .. seealso::
            _export_picking() for picking vals details
            _export_move() for move vals details
        """
        StockMove = self.env['stock.move']
        picking_id = self._extract_param(params, 'picking.id')
        moves = StockMove.search([('picking_id', '=', picking_id)])
        custom_fields = self.with_context(
            picking_id=picking_id)._get_custom_fields_dict()
        return [
            self._export_move(move, custom_fields)
            for move in moves]

    @api.model
    def set_quantity(self, params):
        """ Set done quantity for a given move.
        :param params: {'move': move_vals, 'quantity': integer}
        """
        StockMove = self.env['stock.move']
        move_id = self._extract_param(params, 'move.id')
        qty_done = self._extract_param(params, 'qty_done', 0)
        move = StockMove.search([('id', '=', move_id)])
        if move:
            move.quantity_done = qty_done
        return True

    @api.model
    def try_validate_picking(self, params):
        """ simulate the click on "Validate" button, to know if
        backorder is possible, etc.
        :param params: {'picking': picking_vals}
        """
        StockPicking = self.env['stock.picking']
        picking_id = self._extract_param(params, 'picking.id')
        picking = StockPicking.search([('id', '=', picking_id)])

        res = picking.with_context(
            skip_overprocessed_check=True).button_validate()
        if not res:
            return "picking_validated"
        model = res.get('res_model', False)
        if model == 'stock.immediate.transfer':
            return 'immediate_transfer'
        elif model == 'stock.backorder.confirmation':
            return 'backorder_confirmation'
        else:
            raise UserError(_(
                "incorrect value for model %s" % (model)))

    @api.model
    def confirm_picking(self, params):
        """ Confirm a given picking
        :param params: {
            'picking': picking_vals,
            'action': string,
        }
        action can :
        - 'immediate_transfer' if no quantity has been set
        - 'with_backorder', to create a backorder
        - 'without_backorder', to cancel the backorder
        """

        StockPicking = self.env['stock.picking']
        WizardImmediate = self.env['stock.immediate.transfer']
        WizardBackorder = self.env['stock.backorder.confirmation']

        picking_id = self._extract_param(params, 'picking.id')
        action = self._extract_param(params, 'action')
        picking = StockPicking.search([('id', '=', picking_id)])

        if action == 'immediate_transfer':
            wizard = WizardImmediate.create(
                {'pick_ids': [(6, 0, picking.ids)]})
            wizard.process()
        else:
            wizard = WizardBackorder.create(
                {'pick_ids': [(6, 0, picking.ids)]})
            if action == 'with_backorder':
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
    def _export_move(self, move, custom_fields):
        return {
            'id': move.id,
            'uom': self._export_uom(move.product_uom),
            'product': self._export_product(move.product_id, custom_fields),
            'qty_expected': move.product_uom_qty,
            'qty_done': move.quantity_done,
        }
