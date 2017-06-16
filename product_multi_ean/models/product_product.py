# -*- coding: utf-8 -*-
# © 2012-2014 Guewen Baconnier (Camptocamp SA)
# © 2015 Roberto Lizana (Trey)
# © 2016 Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api, _
from odoo.exceptions import Warning as UserError


class ProductEan13(models.Model):
    _name = 'product.ean13'
    _description = "List of EAN13 for a product."
    _order = 'sequence, id'

    name = fields.Char(string='EAN13', size=13, required=True)
    sequence = fields.Integer(string='Sequence', default=0)
    product_id = fields.Many2one(
        string='Product', comodel_name='product.product', required=True)

    @api.multi
    @api.constrains('name')
    @api.onchange('name')
    def _check_name(self):
        for record in self:
            if record.name and not self.env['barcode.nomenclature'].check_ean(
                                    record.name):
                raise UserError(
                    _('You provided an invalid "EAN13 Barcode" reference. You '
                      'may use the "Internal Reference" field instead.'))

    @api.multi
    @api.constrains('name')
    def _check_duplicates(self):
        for record in self:
            eans = self.search(
                [('id', '!=', record.id), ('name', '=', record.name)])
            if eans:
                raise UserError(
                    _('The EAN13 Barcode "%s" already exists for product '
                      '"%s"') % (record.name, eans[0].product_id.name))


class ProductProduct(models.Model):
    _inherit = 'product.product'

    ean13_ids = fields.One2many(
        comodel_name='product.ean13', inverse_name='product_id',
        string='EAN13')
    ean13 = fields.Char(
        string='Main EAN13', compute='_compute_ean13', store=True,
        inverse='_inverse_ean13', readonly=True)
    barcode = fields.Char(
        'Barcode', copy=False, oldname='ean13', compute='_compute_barcode',
        help="International Article Number used for product identification.",
        readonly=False)

    @api.multi
    @api.depends('ean13_ids')
    def _compute_ean13(self):
        for product in self:
            product.ean13 = product.ean13_ids[:1].name

    @api.multi
    @api.depends('ean13')
    def _compute_barcode(self):
        for product in self:
            product.barcode = product.ean13

    @api.multi
    def _inverse_ean13(self):
        for product in self:
            if product.ean13_ids:
                product.ean13_ids[:1].write({'name': product.ean13})
            else:
                self.env['product.ean13'].create(self._prepare_ean13_vals())

    @api.multi
    def _prepare_ean13_vals(self):
        self.ensure_one()
        return {
            'product_id': self.id,
            'name': self.ean13,
        }

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
