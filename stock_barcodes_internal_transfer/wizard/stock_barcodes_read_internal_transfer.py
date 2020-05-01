# Copyright 2020 Manuel Calero - Xtendoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import _, fields, models
from odoo.exceptions import ValidationError
from odoo.fields import first
from odoo.addons import decimal_precision as dp
from datetime import datetime


class WizStockBarcodesReadInternalTransfer(models.TransientModel):
    _name = 'wiz.stock.barcodes.read.internal.transfer'
    _inherit = 'wiz.stock.barcodes.read'
    _description = 'Wizard to read barcode on internal transfer'

    picking_id = fields.Many2one(
        comodel_name='stock.picking',
        string='Picking',
        readonly=True,
    )
    picking_product_qty = fields.Float(
        string='Picking quantities',
        digits=dp.get_precision('Product Unit of Measure'),
        readonly=True,
    )
    location_dest_id = fields.Many2one(
        "stock.location",
        "Destination Location",
        help="Location where the system will stock the moved products.",
    )

    def name_get(self):
        return [
            (rec.id, '{} - {} - {}'.format(
                _('Barcode reader'),
                rec.picking_id.name,
                self.env.user.name)) for rec in self]

    def _prepare_internal_transfer_move(self):
        return {
            'picking_id': self.picking_id.id,
            'product_id': self.product_id.id,
            'name': self.product_id.name,
            'product_uom': self.product_id.uom_id.id,
            'product_uom_qty': self.product_qty,
            'location_id': self.location_id.id,
            'location_dest_id': self.location_dest_id.id,
            'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'date_expected': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'procure_method': 'make_to_stock',
        }

    def _prepare_internal_transfer_move_line(self, move):
        return {
            'move_id': move.id,
            'lot_id': self.lot_id.id,
            'qty_done': move.product_uom_qty,
            'product_id': move.product_id.id,
            'product_uom_id': move.product_uom.id,
            'location_id': move.location_id.id,
            'location_dest_id': move.location_dest_id.id,
        }

    def _prepare_internal_transfer_move_line_domain(self, log_scan=False):
        record = log_scan or self
        return [
            ('picking_id', '=', self.picking_id.id),
            ('location_id', '=', record.location_id.id),
            ('location_dest_id', '=', record.location_dest_id.id),
            ('product_id', '=', record.product_id.id),
            ('lot_id', '=', record.lot_id.id),
        ]

    def _add_internal_transfer_move(self):
        StockMove = self.env['stock.move']
        StockMoveLine = self.env['stock.move.line']
        line = StockMoveLine.search(
            self._prepare_internal_transfer_move_line_domain(), limit=1
        )
        if line:
            line.write({
                'qty_done': line.qty_done + self.product_qty,
            })
            return
        move = StockMove.create(self._prepare_internal_transfer_move())
        StockMoveLine.create(
            self._prepare_internal_transfer_move_line(move)
        )

    def _prepare_scan_log_values(self, log_detail=False):
        res = super()._prepare_scan_log_values(log_detail)
        res['location_dest_id'] = self.location_dest_id.id
        return res

    def action_done(self):
        result = super().action_done()
        if result:
            self._add_internal_transfer_move()
        return result

    def action_manual_entry(self):
        result = super().action_manual_entry()
        if result:
            self.action_done()
        return result

    def check_done_conditions(self):
        res = super().check_done_conditions()
        if self.product_id.tracking != 'none' and not self.lot_id:
            self._set_messagge_info('info', _('Waiting for input lot'))
            return False
        if not self.picking_id:
            self._set_messagge_info(
                'info', _('Not picking selected'))
            return False
        return res

    def _prepare_scan_log_values(self, log_detail=False):
        # Store in read log line each line added with the quantities assigned
        vals = super()._prepare_scan_log_values(log_detail=log_detail)
        vals['picking_id'] = self.picking_id.id
        return vals

    def action_undo_last_scan(self):
        res = super().action_undo_last_scan()
        log_scan = first(self.scan_log_ids.filtered(
            lambda x: x.create_uid == self.env.user))
        if log_scan:
            move_line = self.env['stock.move.line'].search(
                self._prepare_internal_transfer_move_line_domain(log_scan=log_scan)
            )
            if move_line.picking_id.state == 'done':
                raise ValidationError(_(
                    'You can not remove a scanning log from an validated')
                )
            if move_line:
                qty = move_line.qty_done - log_scan.product_qty
                move_line.qty_done = max(qty, 0.0)
                self.picking_product_qty = move_line.qty_done
        log_scan.unlink()
        return res
