# © 2012-2014 Guewen Baconnier (Camptocamp SA)
# © 2015 Roberto Lizana (Trey)
# © 2016 Pedro M. Baeza
# © 2018 Xavier Jimenez (QubiQ)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class ProductEan13(models.Model):
    _name = 'product.ean13'
    _description = "List of EAN13 for a product."
    _order = 'sequence, id'

    name = fields.Char(
        string='EAN13',
        required=True,
    )
    sequence = fields.Integer(
        string='Sequence',
        default=0,
    )
    product_id = fields.Many2one(
        string='Product',
        comodel_name='product.product',
        required=True,
    )

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
        comodel_name='product.ean13',
        inverse_name='product_id',
        string='EAN13',
    )
    barcode = fields.Char(
        string='Main EAN13',
        compute='_compute_barcode',
        store=True,
        inverse='_inverse_barcode',
        compute_sudo=True,
        inverse_sudo=True,
    )

    @api.multi
    @api.depends('ean13_ids')
    def _compute_barcode(self):
        for product in self:
            product.barcode = product.ean13_ids[:1].name

    @api.multi
    def _inverse_barcode(self):
        for product in self:
            if product.ean13_ids:
                product.ean13_ids[:1].write({'name': product.barcode})
            else:
                self.env['product.ean13'].create(self._prepare_ean13_vals())

    @api.multi
    def _prepare_ean13_vals(self):
        self.ensure_one()
        return {
            'product_id': self.id,
            'name': self.barcode,
        }

    @api.model
    def search(self, domain, *args, **kwargs):
        for sub_domain in list(filter(lambda x: x[0] == 'barcode', domain)):
            domain = self._get_ean13_domain(sub_domain, domain)
        return super(ProductProduct, self).search(domain, *args, **kwargs)

    def _get_ean13_domain(self, sub_domain, domain):
        ean_operator = sub_domain[1]
        ean_value = sub_domain[2]
        eans = self.env['product.ean13'].search(
            [('name', ean_operator, ean_value)])
        domain = [('ean13_ids', 'in', eans.ids)
                  if x[0] == 'barcode' and x[2] == ean_value
                  else x for x in domain]
        return domain
