# Copyright 2019 Sergio Teruel <sergio.teruel@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import _, fields, models
from odoo.fields import first
from odoo.addons import decimal_precision as dp


class WizStockBarcodesReadInventory(models.TransientModel):
    _name = 'wiz.stock.barcodes.read.inventory'
    _inherit = 'wiz.stock.barcodes.read'
    _description = 'Wizard to read barcode on inventory'

    inventory_id = fields.Many2one(
        comodel_name='stock.inventory',
        string='Inventory',
        readonly=True,
    )
    inventory_product_qty = fields.Float(
        string='Inventory quantities',
        digits=dp.get_precision('Product Unit of Measure'),
        readonly=True,
    )

    def name_get(self):
        return [
            (rec.id, '{} - {} - {}'.format(
                _('Barcode reader'),
                rec.inventory_id.name, self.env.user.name)) for rec in self]

    def _prepare_inventory_line(self):
        return {
            'inventory_id': self.inventory_id.id,
            'product_id': self.product_id.id,
            'location_id': self.location_id.id,
            'product_uom_id': self.product_id.uom_id.id,
            'product_qty': self.product_qty,
            'prod_lot_id': self.lot_id.id,
        }

    def _prepare_inventory_line_domain(self, log_scan=False):
        """
        Use the same domain for create or update a stock inventory line.
        Source data is scan log record if undo or wizard model if create or
        update one
        """
        record = log_scan or self
        return [
            ('inventory_id', '=', self.inventory_id.id),
            ('product_id', '=', record.product_id.id),
            ('location_id', '=', record.location_id.id),
            ('prod_lot_id', '=', record.lot_id.id),
        ]

    def _add_inventory_line(self):
        StockInventoryLine = self.env['stock.inventory.line']
        line = StockInventoryLine.search(
            self._prepare_inventory_line_domain(), limit=1)
        if line:
            line.write({
                'product_qty': line.product_qty + self.product_qty,
            })
        else:
            line = StockInventoryLine.create(self._prepare_inventory_line())
        self.inventory_product_qty = line.product_qty

    def check_done_conditions(self):
        if self.product_id.tracking != 'none' and not self.lot_id:
            self._set_messagge_info('info', _('Waiting for input lot'))
            return False
        return super().check_done_conditions()

    def action_done(self):
        result = super().action_done()
        if result:
            self._add_inventory_line()
        return result

    def action_manual_entry(self):
        result = super().action_manual_entry()
        if result:
            self.action_done()
        return result

    def reset_qty(self):
        super().reset_qty()
        self.inventory_product_qty = 0.0

    def action_undo_last_scan(self):
        res = super().action_undo_last_scan()
        log_scan = first(self.scan_log_ids.filtered(
            lambda x: x.create_uid == self.env.user))
        if log_scan:
            inventory_line = self.env['stock.inventory.line'].search(
                self._prepare_inventory_line_domain(log_scan=log_scan))
            if inventory_line:
                qty = inventory_line.product_qty - log_scan.product_qty
                inventory_line.product_qty = qty if qty > 0.0 else 0.0
                self.inventory_product_qty = inventory_line.product_qty
        log_scan.unlink()
        return res
