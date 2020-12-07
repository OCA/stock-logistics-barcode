# © 2012-2014 Guewen Baconnier (Camptocamp SA)
# © 2015 Roberto Lizana (Trey)
# © 2016 Pedro M. Baeza
# © 2018 Xavier Jimenez (QubiQ)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class ProductBarcode(models.Model):
    _name = "product.barcode"
    _description = "Individual item in a product's barcode list"
    _order = "sequence, id"

    name = fields.Char(string="Barcode", required=True,)
    sequence = fields.Integer(string="Sequence", default=0,)
    product_id = fields.Many2one(
        string="Product", comodel_name="product.product",
        compute='_compute_product', store=True,
        readonly=False,
    )
    product_tmpl_id = fields.Many2one(
        comodel_name="product.template",
        compute='_compute_product_tmpl', store=True,
        readonly=False,
    )

    @api.depends('product_id')
    def _compute_product_tmpl(self):
        for rec in self.filtered(lambda x: not x.product_tmpl_id and x.product_id):
            rec.product_tmpl_id = rec.product_id.product_tmpl_id

    @api.depends('product_tmpl_id.product_variant_ids')
    def _compute_product(self):
        for rec in self.filtered(lambda x: not x.product_id and x.product_tmpl_id.product_variant_ids):
            rec.product_id = rec.product_tmpl_id.product_variant_ids[0]

    @api.constrains("name")
    def _check_duplicates(self):
        for record in self:
            barcodes = self.search(
                [("id", "!=", record.id), ("name", "=", record.name)]
            )
            if barcodes:
                raise UserError(
                    _('The Barcode "%s" already exists for product ' '"%s"')
                    % (record.name, barcodes[0].product_id.name)
                )


class ProductTemplate(models.Model):
    _inherit = "product.template"

    barcode_ids = fields.One2many(
        comodel_name="product.barcode", inverse_name="product_tmpl_id", string="Barcodes",
    )


class ProductProduct(models.Model):
    _inherit = "product.product"

    barcode_ids = fields.One2many(
        comodel_name="product.barcode",
        inverse_name="product_id",
        string="Barcodes",
    )
    barcode = fields.Char(
        string="Main barcode",
        compute="_compute_barcode",
        store=True,
        inverse="_inverse_barcode",
        compute_sudo=True,
        inverse_sudo=True,
    )

    @api.depends("barcode_ids.name", "barcode_ids.sequence")
    def _compute_barcode(self):
        for product in self:
            product.barcode = product.barcode_ids[:1].name

    def _inverse_barcode(self):
        for product in self:
            if product.barcode_ids:
                product.barcode_ids[:1].write({"name": product.barcode})
            if not product.barcode:
                product.barcode_ids.unlink()
            else:
                self.env["product.barcode"].create(self._prepare_barcode_vals())

    def _prepare_barcode_vals(self):
        self.ensure_one()
        return {
            "product_id": self.id,
            "name": self.barcode,
        }

    @api.model
    def _search(self, domain, *args, **kwargs):
        for sub_domain in list(filter(lambda x: x[0] == "barcode", domain)):
            domain = self._get_barcode_domain(sub_domain, domain)
        return super(ProductProduct, self)._search(domain, *args, **kwargs)

    def _get_barcode_domain(self, sub_domain, domain):
        barcode_operator = sub_domain[1]
        barcode_value = sub_domain[2]
        barcodes = self.env["product.barcode"].search(
            [("name", barcode_operator, barcode_value)]
        )
        domain = [
            ("barcode_ids", "in", barcodes.ids)
            if x[0] == "barcode" and x[2] == barcode_value
            else x
            for x in domain
        ]
        return domain
