# -*- coding: utf-8 -*-
# Copyright 2019 Sergio Teruel <sergio.teruel@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import logging
from odoo import api, _, fields, models
from odoo.tools.float_utils import float_compare
from odoo.exceptions import ValidationError
from odoo.fields import first
from odoo.addons import decimal_precision as dp

_logger = logging.getLogger(__name__)


class WizStockBarcodesReadPicking(models.TransientModel):
    _name = 'wiz.stock.barcodes.read.picking'
    _inherit = 'wiz.stock.barcodes.read'
    _description = 'Wizard to read barcode on picking'

    picking_id = fields.Many2one(
        comodel_name='stock.picking',
        string='Picking',
    )
    picking_product_qty = fields.Float(
        string='Picking quantities',
        digits=dp.get_precision('Product Unit of Measure'),
        readonly=True,
    )
    picking_type_code = fields.Selection([
        ('incoming', 'Vendors'),
        ('outgoing', 'Customers'),
        ('internal', 'Internal'),
    ], 'Type of Operation')
    confirmed_moves = fields.Boolean(
        string='Confirmed moves',
    )
    name = fields.Char(
        related='picking_id.name',
        readonly=True,
        string='Picking',
    )
    partner_id = fields.Many2one(
        comodel_name='res.partner',
        related='picking_id.partner_id',
        readonly=True,
        string='Partner',
    )
    state = fields.Selection(
        related='picking_id.state',
        readonly=True,
    )
    date = fields.Datetime(
        related='picking_id.date',
        readonly=True,
        string='Creation Date',
    )
    product_qty_reserved = fields.Float(
        'Reserved', compute='_compute_picking_quantity',
        digits=dp.get_precision('Product Unit of Measure'),
        readonly=True,
    )
    product_uom_qty = fields.Float(
        'Demand', compute='_compute_picking_quantity',
        digits=dp.get_precision('Product Unit of Measure'),
        readonly=True,
    )
    product_qty_done = fields.Float(
        'Done', compute='_compute_picking_quantity',
        digits=dp.get_precision('Product Unit of Measure'),
        readonly=True,
    )
    scan_count = fields.Integer()

    @api.depends('picking_id', 'scan_count')
    def _compute_picking_quantity(self):
        qty_reserved = 0
        qty_demand = 0
        qty_done = 0
        if self.picking_id:
            self.product_qty_reserved = sum(self.picking_id.mapped(
                'move_lines.reserved_availability'))
            for move in self.picking_id.move_lines:
                qty_reserved += move.reserved_availability
                qty_demand += move.product_uom_qty
                qty_done += sum(move.linked_move_operation_ids.mapped(
                    'operation_id').mapped('qty_done'))
            self.update({
                'product_qty_reserved': qty_reserved,
                'product_uom_qty': qty_demand,
                'product_qty_done': qty_done,
            })

    def name_get(self):
        return [
            (rec.id, '{} - {} - {}'.format(
                _('Barcode reader'),
                rec.picking_id.name or
                rec.picking_type_code, self.env.user.name)) for rec in self]

    @api.onchange('product_id')
    def onchange_product_id(self):
        res = super(WizStockBarcodesReadPicking, self).onchange_product_id()
        if self.product_id:
            candidate_picking_ids = self.env['stock.pack.operation'].search(
                [('product_id', '=', self.product_id.id)]).mapped('picking_id')
            if self.picking_id not in candidate_picking_ids:
                self.picking_id = False
            return {'domain': {'picking_id': [
                ('id', 'in', candidate_picking_ids.ids)]}}
        return res

    # def _set_default_picking(self):
    #     picking_id = self.env.context.get('default_picking_id', False)
    #     if picking_id:
    #         self._set_candidate_pickings(
    #             self.env['stock.picking'].browse(picking_id))

    # @api.model
    # def create(self, vals):
    #     # When user click any view button the wizard record is create and the
    #     # picking candidates have been lost, so we need set it.
    #     wiz = super(WizStockBarcodesReadPicking, self).create(vals)
    #     if wiz.picking_id:
    #         wiz._set_candidate_pickings(wiz.picking_id)
    #     return wiz

    # @api.onchange('picking_id')
    # def onchange_picking_id(self):
    #     # Add to candidate pickings the default picking. We are in a wizard
    #     # view, so for create a candidate picking with the same default picking
    #     # we need create it in this onchange
    #     self._set_default_picking()

    def action_done(self):
        if self.check_done_conditions():
            res = self._process_stock_move_line()
            if res:
                self._add_read_log(res)
                self.scan_count += 1

    def action_manual_entry(self):
        result = super(WizStockBarcodesReadPicking, self).action_manual_entry()
        if result:
            self.action_done()
        return result

    def _prepare_pack_operation_values(self, candidate_move, available_qty):
        pack_lot_ids = self.env['stock.pack.operation.lot'].search(
            [('lot_id', '=', self.lot_id.id)]).ids
        return {
            'picking_id': self.picking_id.id,
            'qty_done': available_qty,
            'product_uom_id': self.product_id.uom_po_id.id,
            'product_id': self.product_id.id,
            'location_id': self.picking_id.location_id.id,
            'location_dest_id': self.location_id.id,
            'pack_lot_ids': [(6, 0, pack_lot_ids)]
        }

    def _states_move_allowed(self):
        move_states = ['assigned']
        if self.confirmed_moves:
            move_states.append('confirmed')
        return move_states

    def _prepare_stock_pack_operation_domain(self):
        domain = [
            ('product_id', '=', self.product_id.id),
            ('picking_id.picking_type_id.code', '=', self.picking_type_code),
            ('state', 'in', self._states_move_allowed()),
        ]
        if self.picking_id:
            domain.append(('picking_id', '=', self.picking_id.id))
        return domain

    # def _set_candidate_pickings(self, candidate_pickings):
    #     # vals = [(5, 0, 0)]
    #     # vals.extend([(0, 0, {
    #     #     'picking_id': p.id,
    #     # }) for p in candidate_pickings])
    #     # self.candidate_picking_ids = vals
    #     self.env['wiz.candidate.picking'].search([]).unlink()
    #     for picking in candidate_pickings:
    #         self.env['wiz.candidate.picking'].create({
    #             'picking_id': picking.id,
    #         })

    # def _search_candidate_pickings(self, operations=False):
    #     if not operations:
    #         operations = self.env['stock.pack.operation'].search(
    #             self._prepare_stock_pack_operation_domain())
    #     if not self.picking_id:
    #         candidate_pickings = operations.mapped('picking_id')
    #         candidate_pickings_count = len(candidate_pickings)
    #         if candidate_pickings_count > 1:
    #             self._set_candidate_pickings(candidate_pickings)
    #             return False
    #         if candidate_pickings_count == 1:
    #             self.picking_id = candidate_pickings
    #             self._set_candidate_pickings(candidate_pickings)
    #         _logger.info('No picking assigned')
    #     return True

    def _process_stock_move_line(self):
        """
        Search assigned or confirmed stock moves from a picking operation type
        or a picking. If there is more than one picking with demand from
        scanned product the interface allow to select what picking to work.
        If only there is one picking the scan data is assigned to it.
        """
        StockPackOperation = self.env['stock.pack.operation']
        operations = StockPackOperation.search(
            self._prepare_stock_pack_operation_domain())
        # if not self._search_candidate_pickings(operations):
        #     return False
        available_qty = self.product_qty
        move_lines_dic = {}
        for operation in operations:
            if operation.product_qty:
                assigned_qty = min(
                    max(operation.product_qty - operation.qty_done, 0.0),
                    available_qty)
            else:
                assigned_qty = available_qty
            if operation.product_id.tracking != 'none':
                operation_lot = self.env[
                    'stock.pack.operation.lot'].search(
                    [('operation_id', '=', operation.id),
                     ('lot_id', '=', self.lot_id.id)])
                if operation_lot and operation.product_id.tracking == 'lot':
                    operation_lot.write(
                        {'qty': operation_lot.qty + assigned_qty})
                elif not operation_lot or \
                        (operation_lot and
                         operation.product_id.tracking == 'serial'):
                    self.env['stock.pack.operation.lot'].create({
                        'operation_id': operation.id,
                        'lot_id': self.lot_id.id,
                        'lot_name': self.lot_id.name,
                        'qty': assigned_qty,
                    })
                operation.write({'qty_done': sum(
                    [x.qty for x in operation.pack_lot_ids])})
            else:
                operation.write(
                    {'qty_done': operation.qty_done + assigned_qty})
            available_qty -= assigned_qty
            if assigned_qty:
                move_lines_dic[operation.id] = assigned_qty
            if float_compare(
                    available_qty, 0.0,
                    precision_rounding=operation.product_id.uom_id.
                    rounding) < 1:
                break
        if float_compare(
                available_qty, 0,
                precision_rounding=self.product_id.uom_id.rounding) > 0:
            # Create an extra pack operation if this product has an
            # initial demand.
            moves = self.picking_id.move_lines.filtered(lambda m: (
                m.product_id == self.product_id and
                m.state in self._states_move_allowed()))
            if not moves:
                # TODO: Add picking if picking_id to message
                self._set_message_info(
                    'info',
                    _('There are no stock moves to assign this operation'))
                return False
            else:
                line = StockPackOperation.create(
                    self._prepare_pack_operation_values(
                        moves[0], available_qty))
                move_lines_dic[line.id] = available_qty
        self.picking_product_qty = sum(operations.mapped('qty_done'))
        return move_lines_dic

    # def _candidate_picking_selected(self):
    #     if self.candidate_picking_id:
    #         return self.candidate_picking_id.picking_id
    #     else:
    #         return self.env['stock.picking'].browse()

    def check_done_conditions(self):
        res = super(WizStockBarcodesReadPicking, self).check_done_conditions()
        if self.product_id.tracking != 'none' and not self.lot_id:
            self._set_message_info('info', _('Waiting for input lot'))
            return False
        if not self.picking_id:
            self._set_message_info(
                'info', _('Please, select the picking'))
            return False
            # if not self._search_candidate_pickings():
            #     self._set_message_info(
            #         'info', _('Click on picking pushpin to lock it'))
            #     return False
        # if self.picking_id != self._candidate_picking_selected():
        #     self._set_message_info(
        #         'info', _('Click on picking pushpin to lock it'))
        #     return False
        return res

    def _prepare_scan_log_values(self, log_detail=False):
        # Store in read log line each line added with the quantities assigned
        vals = super(WizStockBarcodesReadPicking, self).\
            _prepare_scan_log_values(log_detail=log_detail)
        vals['picking_id'] = self.picking_id.id
        if log_detail:
            vals['log_line_ids'] = [(0, 0, {
                'pack_operation_id': x[0],
                'product_qty': x[1],
            }) for x in log_detail.items()]
        return vals

    def remove_scanning_log(self, scanning_log):
        for log in scanning_log:
            for log_scan_line in log.log_line_ids:
                if log_scan_line.pack_operation_id.state not in ['assigned',
                                                                 'confirmed']:
                    raise ValidationError(_(
                        'You can not remove an entry linked to a stock move '
                        'line in state assigned or confirmed')
                    )
                qty = (log_scan_line.pack_operation_id.qty_done -
                       log_scan_line.product_qty)
                log_scan_line.pack_operation_id.qty_done = max(qty, 0.0)
            self.picking_product_qty = sum(log.log_line_ids.mapped(
                'pack_operation_id.qty_done'))
            log.unlink()

    def action_undo_last_scan(self):
        res = super(WizStockBarcodesReadPicking, self).action_undo_last_scan()
        log_scan = first(self.scan_log_ids.filtered(
            lambda x: x.create_uid == self.env.user))
        self.remove_scanning_log(log_scan)
        return res


class WizCandidatePicking(models.Model):
    """
    TODO: explain
    """
    _name = 'wiz.candidate.picking'
    _description = 'Candidate pickings for barcode interface'
    # To prevent remove the record wizard until 2 days old
    # _transient_max_hours = 48

    picking_id = fields.Many2one(
        comodel_name='stock.picking',
        string='Picking',
        readonly=True,
    )
    name = fields.Char(
        related='picking_id.name',
        readonly=True,
        string='Picking',
    )
    partner_id = fields.Many2one(
        comodel_name='res.partner',
        related='picking_id.partner_id',
        readonly=True,
        string='Partner',
    )
    state = fields.Selection(
        related='picking_id.state',
        readonly=True,
    )
    date = fields.Datetime(
        related='picking_id.date',
        readonly=True,
        string='Creation Date',
    )
    product_qty_reserved = fields.Float(
        'Reserved', compute='_compute_picking_quantity',
        digits=dp.get_precision('Product Unit of Measure'),
        readonly=True,
    )
    product_uom_qty = fields.Float(
        'Demand', compute='_compute_picking_quantity',
        digits=dp.get_precision('Product Unit of Measure'),
        readonly=True,
    )
    product_qty_done = fields.Float(
        'Done', compute='_compute_picking_quantity',
        digits=dp.get_precision('Product Unit of Measure'),
        readonly=True,
    )
    # For reload kanban view
    scan_count = fields.Integer()

    @api.depends('scan_count')
    def _compute_picking_quantity(self):
        for candidate in self:
            qty_reserved = 0
            qty_demand = 0
            qty_done = 0
            candidate.product_qty_reserved = sum(candidate.picking_id.mapped(
                'move_lines.reserved_availability'))
            for move in candidate.picking_id.move_lines:
                qty_reserved += move.reserved_availability
                qty_demand += move.product_uom_qty
                qty_done += sum(move.linked_move_operation_ids.mapped(
                    'operation_id').mapped('qty_done'))
            candidate.update({
                'product_qty_reserved': qty_reserved,
                'product_uom_qty': qty_demand,
                'product_qty_done': qty_done,
            })

    def _get_wizard_barcode_read(self):
        # return self.env['wiz.stock.barcodes.read.picking'].browse(
        #     self.env.context['wiz_barcode_id'])
        return self.env['wiz.stock.barcodes.read.picking'].search([], limit=1)

    def action_lock_picking(self):
        # wiz = self._get_wizard_barcode_read()
        # picking_id = self.env.context['picking_id']
        # wiz.picking_id = picking_id
        # wiz._set_candidate_pickings(wiz.picking_id)
        # return wiz.action_done()
        return

    def action_unlock_picking(self):
        wiz = self._get_wizard_barcode_read()
        wiz.update({
            'picking_id': False,
            'candidate_picking_id': False,
            'message_type': False,
            'message': False,
        })
        return wiz.action_cancel()

    def action_validate_picking(self):
        picking = self.env['stock.picking'].browse(
            self.env.context.get('picking_id', False)
        )
        return picking.button_validate()
