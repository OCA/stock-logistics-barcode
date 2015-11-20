# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields, api, exceptions, _
from openerp.addons.product import product as addons_product


class ProductEan13(models.Model):
    _name = 'product.ean13'
    _description = "List of EAN13 for a product."
    _order = 'sequence'

    name = fields.Char(string='EAN13', size=13, required=True)
    sequence = fields.Integer(string='Sequence')
    product_id = fields.Many2one(
        string='Product',
        comodel_name='product.product',
        required=True)

    @api.onchange('name')
    def onchange_name(self):
        if not addons_product.check_ean(self.name):
            raise exceptions.Warning(_(
                'You provided an invalid "EAN13 Barcode" reference. You may '
                'use the "Internal Reference" field instead.'))

    @api.one
    @api.constrains('name')
    def _check_name(self):
        if not addons_product.check_ean(self.name):
            raise exceptions.Warning(_(
                'You provided an invalid "EAN13 Barcode" reference. You may '
                'use the "Internal Reference" field instead.'))
        eans = self.search([('id', '!=', self.id), ('name', '=', self.name)])
        if eans:
            raise exceptions.Warning(_(
                'The EAN13 Barcode "%s" already exists for product "%s"!') % (
                    self.name, eans[0].product_id.name))

    def _auto_init(self, cr, context=None):
        exist = self._table_exist(cr)
        res = super(ProductEan13, self)._auto_init(cr, context=context)
        if not exist:
            cr.execute('INSERT INTO %s (product_id, name, sequence) '
                       'SELECT id, ean13, 0 '
                       'FROM product_product '
                       'WHERE ean13 != \'\'' % self._table)
        return res


class ProductProduct(models.Model):
    _inherit = 'product.product'

    ean13_ids = fields.One2many(
        comodel_name='product.ean13',
        inverse_name='product_id',
        string='EAN13')
    ean13 = fields.Char(
        string='Main EAN13',
        compute='_compute_ean13',
        store=True)

    @api.one
    @api.depends('ean13_ids')
    def _compute_ean13(self):
        if self.ean13_ids:
            if self.ean13 != self.ean13_ids[0]:
                self.ean13 = self.ean13_ids[0].name
        else:
            self.ean13 = ''

    @api.one
    def _create_ean13(self, ean13):
        return self.env['product.ean13'].create({
            'product_id': self.id,
            'ean13': ean13})

    @api.model
    def create(self, vals):
        res = super(ProductProduct, self).create(vals)
        if 'ean13' in vals:
            self._create_ean13(res.ean13)
        return res

    @api.one
    def write(self, vals):
        if 'ean13' in vals:
            eans = [e for e in self.ean13_ids if e.name == self.ean13]
            if eans:
                eans.write({'name': vals['ean13']})
            else:
                self._create_ean13(vals['ean13'])
        return super(ProductProduct, self).write(vals)

    @api.model
    def search(self, domain, *args, **kwargs):
        if filter(lambda x: x[0] == 'ean13', domain):
            ean_operator = filter(lambda x: x[0] == 'ean13', domain)[0][1]
            ean_value = filter(lambda x: x[0] == 'ean13', domain)[0][2]
            eans = self.env['product.ean13'].search(
                [('name', ean_operator, ean_value)])
            domain = filter(lambda x: x[0] != 'ean13', domain)
            domain += [('ean13_ids', 'in', eans.ids)]
        return super(ProductProduct, self).search(domain, *args, **kwargs)
