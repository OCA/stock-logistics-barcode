# Copyright 2019 Sergio Teruel <sergio.teruel@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import logging
from odoo import api, _, fields, models
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
        readonly=True,
    )
    candidate_picking_ids = fields.One2many(
        comodel_name='wiz.candidate.picking',
        inverse_name='wiz_barcode_id',
        string='Candidate pickings',
        readonly=True,
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

    def name_get(self):
        return [
            (rec.id, '{} - {} - {}'.format(
                _('Barcode reader'),
                rec.picking_id.name, self.env.user.name)) for rec in self]

    def _set_default_picking(self):
        picking_id = self.env.context.get('default_picking_id', False)
        if picking_id:
            self._set_candidate_pickings(
                self.env['stock.picking'].browse(picking_id))

    @api.model
    def create(self, vals):
        # When user click any view button the wizard record is create and the
        # picking candidates have been lost, so we need set it.
        wiz = super().create(vals)
        wiz._set_default_picking()
        return wiz

    @api.onchange('picking_id')
    def onchange_picking_id(self):
        # Add to candidate pickings the default picking. We are in a wizard
        # view, so for create a candidate picking with the same default picking
        # we need create it in this onchange
        self._set_default_picking()

    def action_done(self):
        if self.check_done_conditions():
            if self._process_stock_move_line():
                return super().action_done()

    def action_manual_entry(self):
        result = super().action_manual_entry()
        if result:
            self.action_done()
        return result

    def _prepare_move_line_values(self, candidate_move):
        return {
            'picking_id': self.picking_id.id,
            'move_id': candidate_move.id,
            'qty_done': self.product_qty,
            'product_uom_id': self.product_id.uom_po_id.id,
            'product_id': self.product_id.id,
            'location_id': self.picking_id.location_id.id,
            'location_dest_id': self.location_id.id,
            'lot_id': self.lot_id.id,
            'lot_name': self.lot_id.name,
        }

    def _prepare_stock_moves_domain(self):
        domain = [
            ('product_id', '=', self.product_id.id),
            ('state', '=', 'assigned'),
            ('picking_id.picking_type_id.code', '=', self.picking_type_code),
        ]
        if self.picking_id:
            domain.append(('picking_id', '=', self.picking_id.id))
        return domain

    def _set_candidate_pickings(self, candidate_pickings):
        vals = [(5, 0, 0)]
        vals.extend([(0, 0, {
            'picking_id': p.id,
        }) for p in candidate_pickings])
        self.candidate_picking_ids = vals

    def _search_candidate_pickings(self, moves_todo=False):
        if not moves_todo:
            moves_todo = self.env['stock.move'].search(
                self._prepare_stock_moves_domain())
        if not self.picking_id:
            candidate_pickings = moves_todo.mapped('picking_id')
            candidate_pickings_count = len(candidate_pickings)
            if candidate_pickings_count > 1:
                self.select_cadidate_picking(candidate_pickings)
                return False
            if candidate_pickings_count == 1:
                self.picking_id = candidate_pickings
                self._set_candidate_pickings(candidate_pickings)
            _logger.info('No picking assigned')
        return True

    def _process_stock_move_line(self):
        """
        Search assigned stock moves from a picking operation type or a picking.
        If there is more than one picking with demand from scanned product the
        interface allow to select what picking to work.
        If only there is one picking the scan data is assigned to it.
        """
        StockMove = self.env['stock.move']
        StockMoveLine = self.env['stock.move.line']
        moves_todo = StockMove.search(self._prepare_stock_moves_domain())
        if not self._search_candidate_pickings(moves_todo):
            return False
        lines = moves_todo.mapped('move_line_ids').filtered(
            lambda l: (l.picking_id == self.picking_id and
                       l.product_id == self.product_id and
                       l.lot_id == self.lot_id))
        move_line = StockMoveLine.browse()
        if lines:
            qty_assigned = 0.0
            lines_count = len(lines)
            for index, line in enumerate(lines):
                if index + 1 < lines_count:
                    qty_need = line.product_uom_qty - line.qty_done
                    if self.product_qty < qty_need:
                        qty_assigned = self.product_qty
                    else:
                        qty_assigned = qty_need
                    line.qty_done += qty_assigned
                else:
                    line.qty_done += self.product_qty - qty_assigned
            self.update_quantity_done(lines)
        else:
            # Create an extra stock move line if this product has an
            # initial demand.
            moves = self.picking_id.move_lines.filtered(lambda m: (
                m.product_id == self.product_id and m.state == 'assigned'))
            if not moves:
                self._set_messagge_info(
                    'info',
                    _('There are no stock moves to assign this operation'))
                return False
            else:
                vals = self._prepare_move_line_values(moves[0])
                move_line = StockMoveLine.create(vals)
            self.update_quantity_done(move_line)
        return True

    def update_quantity_done(self, move_lines):
        self.picking_product_qty = sum(
            move_lines.mapped('move_id.quantity_done'))

    def select_cadidate_picking(self, picking_candidates):
        self._set_candidate_pickings(picking_candidates)

    def _candidate_picking_selected(self):
        if len(self.candidate_picking_ids) == 1:
            return self.candidate_picking_ids.picking_id
        else:
            return self.env['stock.picking'].browse()

    def check_done_conditions(self):
        res = super().check_done_conditions()
        if self.product_id.tracking != 'none' and not self.lot_id:
            self._set_messagge_info('info', _('Waiting for input lot'))
            return False
        if not self.picking_id:
            if not self._search_candidate_pickings():
                self._set_messagge_info('info', _('Select one picking'))
                return False
        if self.picking_id != self._candidate_picking_selected():
            self._set_messagge_info('info', _('Select one picking'))
            return False
        return res

    def _prepare_move_line_undo_domain(self, log_scan=False):
        return [
            ('picking_id', '=', log_scan.picking_id.id),
            ('product_id', '=', log_scan.product_id.id),
            ('lot_id', '=', log_scan.lot_id.id),
            ('move_id.picking_id.picking_type_id.code', '=',
             self.env.context.get('default_picking_type_code')),
            ('state', '=', 'assigned'),
        ]

    def action_undo_last_scan(self):
        res = super().action_undo_last_scan()
        log_scan = first(self.scan_log_ids.filtered(
            lambda x: x.create_uid == self.env.user))
        if log_scan:
            domain = self._prepare_move_line_undo_domain(log_scan=log_scan)
            lines = self.env['stock.move.line'].search(domain)
            undo_qty = 0.0
            for line in lines:
                qty = line.qty_done - log_scan.product_qty
                undo_qty += line.qty_done
                line.qty_done = qty if qty > 0.0 else 0.0
                if undo_qty == log_scan.product_qty:
                    break
            self.update_quantity_done(lines)
            log_scan.unlink()
        return res

    def _prepare_scan_log_values(self):
        vals = super()._prepare_scan_log_values()
        vals['picking_id'] = self.picking_id.id
        return vals


class WizStockBarcodesCandidatePicking(models.TransientModel):
    _name = 'wiz.candidate.picking'
    _description = 'Candidate pickings for barcode interface'

    wiz_barcode_id = fields.Many2one(
        comodel_name='wiz.stock.barcodes.read.picking',
        readonly=True,
    )
    picking_id = fields.Many2one(
        comodel_name='stock.picking',
        string='Picking',
        readonly=True,
    )
    wiz_picking_id = fields.Many2one(
        comodel_name='stock.picking',
        related='wiz_barcode_id.picking_id',
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

    def _get_wizard_barcode_read(self):
        return self.env['wiz.stock.barcodes.read.picking'].browse(
            self.env.context['wiz_read_scan_id'])

    def action_lock_picking(self):
        wiz = self._get_wizard_barcode_read()
        wiz.update({
            'picking_id': self.picking_id.id,
        })
        wiz._set_candidate_pickings(self.picking_id)
        return wiz.action_done()

    def action_unlock_picking(self):
        wiz = self._get_wizard_barcode_read()
        wiz.update({
            'picking_id': False,
            'candidate_picking_ids': False,
            'message_type': False,
            'message': False,
        })
        return wiz.action_cancel()

    def action_validate_picking(self):
        return self.picking_id.button_validate()
