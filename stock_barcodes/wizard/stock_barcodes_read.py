# Copyright 2019 Sergio Teruel <sergio.teruel@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import _, api, fields, models
from odoo.addons import decimal_precision as dp


class WizStockBarcodesRead(models.AbstractModel):
    _name = 'wiz.stock.barcodes.read'
    _inherit = 'barcodes.barcode_events_mixin'
    _description = 'Wizard to read barcode'
    # To prevent remove the record wizard until 2 days old
    _transient_max_hours = 48

    barcode = fields.Char()
    res_model_id = fields.Many2one(
        comodel_name='ir.model',
        index=True,
    )
    res_id = fields.Integer(index=True)
    product_id = fields.Many2one(
        comodel_name='product.product',
        string='Product',
    )
    lot_id = fields.Many2one(
        comodel_name='stock.production.lot',
        string='Lot',
    )
    location_id = fields.Many2one(
        comodel_name='stock.location',
        string='Location',
    )
    packaging_id = fields.Many2one(
        comodel_name='product.packaging',
        string='Packaging',
    )
    packaging_qty = fields.Float(
        string='Package Qty',
        digits=dp.get_precision('Product Unit of Measure'),
    )
    product_qty = fields.Float(
        string='Product Qty',
        digits=dp.get_precision('Product Unit of Measure'),
    )
    manual_entry = fields.Boolean(
        string='Manual entry data',
    )
    # Computed field for display all scan logs from res_model and res_id when
    # change product_id
    scan_log_ids = fields.Many2many(
        comodel_name='stock.barcodes.read.log',
        compute='_compute_scan_log_ids',
    )
    message_type = fields.Selection([
        ('info', 'Barcode read with additional info'),
        ('not_found', 'No barcode found'),
        ('more_match', 'More than one matches found'),
        ('success', 'Barcode read correctly'),
    ], readonly=True)
    message = fields.Char(readonly=True)

    @api.onchange('location_id')
    def onchange_location_id(self):
        self.packaging_id = False
        self.product_id = False

    @api.onchange('packaging_qty')
    def onchange_packaging_qty(self):
        if self.packaging_id:
            self.product_qty = self.packaging_qty * self.packaging_id.qty

    def _set_messagge_info(self, type, messagge):
        """
        Set message type and message description.
        For manual entry mode barcode is not set so is not displayed
        """
        self.message_type = type
        if self.barcode:
            self.message = _('Barcode: %s (%s)') % (self.barcode, messagge)
        else:
            self.message = '%s' % messagge

    def process_barcode(self, barcode):
        self._set_messagge_info('success', _('Barcode read correctly'))
        domain = self._barcode_domain(barcode)
        product = self.env['product.product'].search(domain)
        if product:
            if len(product) > 1:
                self._set_messagge_info(
                    'more_match', _('More than one product found'))
                return
            self.action_product_scaned_post(product)
            self.action_done()
            return
        if self.env.user.has_group('product.group_stock_packaging'):
            packaging = self.env['product.packaging'].search(domain)
            if packaging:
                if len(packaging) > 1:
                    self._set_messagge_info(
                        'more_match', _('More than one package found'))
                    return
                self.action_packaging_scaned_post(packaging)
                self.action_done()
                return
        if self.env.user.has_group('stock.group_production_lot'):
            lot = self.env['stock.production.lot'].search([
                ('name', '=', barcode),
                ('product_id', '=', self.product_id.id),
            ])
            if lot:
                self.action_lot_scaned_post(lot)
                self.action_done()
                return
        location = self.env['stock.location'].search(domain)
        if location:
            self.location_id = location
            self._set_messagge_info('info', _('Waiting product'))
            return
        self._set_messagge_info('not_found', _('Barcode not found'))

    def _barcode_domain(self, barcode):
        return [('barcode', '=', barcode)]

    def on_barcode_scanned(self, barcode):
        self.barcode = barcode
        self.reset_qty()
        self.process_barcode(barcode)

    def check_done_conditions(self):
        if not self.product_qty:
            self._set_messagge_info('info', _('Waiting quantities'))
            return False
        if self.manual_entry:
            self._set_messagge_info('success', _('Manual entry OK'))
        return True

    def action_done(self):
        if not self.check_done_conditions():
            return False
        self._add_read_log()
        return True

    def action_cancel(self):
        return True

    def action_product_scaned_post(self, product):
        self.packaging_id = False
        if self.product_id != product:
            self.lot_id = False
        self.product_id = product
        self.product_qty = 0.0 if self.manual_entry else 1.0

    def action_packaging_scaned_post(self, packaging):
        self.packaging_id = packaging
        if self.product_id != packaging.product_id:
            self.lot_id = False
        self.product_id = packaging.product_id
        self.packaging_qty = 0.0 if self.manual_entry else 1.0
        self.product_qty = packaging.qty * self.packaging_qty

    def action_lot_scaned_post(self, lot):
        self.lot_id = lot
        self.product_qty = 0.0 if self.manual_entry else 1.0

    def action_clean_lot(self):
        self.lot_id = False

    def action_manual_entry(self):
        return True

    def _prepare_scan_log_values(self):
        return {
            'name': self.barcode,
            'location_id': self.location_id.id,
            'product_id': self.product_id.id,
            'packaging_id': self.packaging_id.id,
            'lot_id': self.lot_id.id,
            'packaging_qty': self.packaging_qty,
            'product_qty': self.product_qty,
            'manual_entry': self.manual_entry,
            'res_model_id': self.res_model_id.id,
            'res_id': self.res_id,
        }

    def _add_read_log(self):
        if self.product_qty:
            vals = self._prepare_scan_log_values()
            self.env['stock.barcodes.read.log'].create(vals)

    @api.depends('product_id', 'lot_id')
    def _compute_scan_log_ids(self):
        logs = self.env['stock.barcodes.read.log'].search([
            ('res_model_id', '=', self.res_model_id.id),
            ('res_id', '=', self.res_id),
            ('location_id', '=', self.location_id.id),
            ('product_id', '=', self.product_id.id),
        ], limit=10)
        self.scan_log_ids = logs

    def reset_qty(self):
        self.product_qty = 0
        self.packaging_qty = 0

    def action_undo_last_scan(self):
        return True
