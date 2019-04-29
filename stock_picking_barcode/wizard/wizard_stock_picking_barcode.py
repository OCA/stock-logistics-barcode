# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models, _


class WizardStockPickingBarcode(models.TransientModel):
    _name = "wizard.stock.picking.barcode"
    _inherit = "barcodes.barcode_events_mixin"

    picking_id = fields.Many2one(
        'stock.picking',
        required=True
    )
    status = fields.Text(
        readonly=1,
        default="Start scanning",
    )
    status_state = fields.Integer(
        default=0,
        readonly=1,
    )
    lot_id = fields.Many2one(
        'stock.production.lot',
        computed='on_barcode_scanned',
    )
    processed_lines = fields.Many2many(
        'stock.production.lot',
        computed='on_barcode_scanned',
    )

    def _show_lines(self):
        show_lines = _("The following lots have been processed from "
                       "Picking %s:\n") % self.lot_id.name
        for line in self.processed_lines:
            show_lines = "%s %s [%s]\n" % (
                show_lines, line.product_id.name, line.order_id.name)
        return show_lines + _("Scan the next barcode or press Close to "
                              "finish scanning.")

    def on_barcode_scanned(self, barcode):
        self.lot_id = self.env['stock.production.lot'].search([
            ('name', '=', barcode)
        ], limit=1)
        if not self.lot_id:
            self.status = _("Barcode %s does not correspond to any "
                            "Lot/Serial Number. Try with another barcode or "
                            "press Close to finish scanning.") % barcode
            self.status_state = 1
            return
        else:
            self.status = _("Barcode %s does correspond to a Lot/serial "
                            "Number") % barcode
            self.status_state = 0
            move = self.env['stock.move'].search([
                ('picking_id', '=', self.picking_id.id),
                ('product_id', '=', self.lot_id.product_id.id),
            ])
            self.env['stock.move.line'].create({
                'location_id': move.location_id.id,
                'location_dest_id': move.location_dest_id.id,
                'picking_id': move.picking_id.id,
                'product_id': move.product_id.id,
                'qty_done': 1,
                'product_uom_id': move.product_id.uom_id.id,
                'lot_id': self.lot_id.id,
                'move_id': move.id,
            })
            return

    @api.multi
    def action_cancel(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_view_reload',
        }
