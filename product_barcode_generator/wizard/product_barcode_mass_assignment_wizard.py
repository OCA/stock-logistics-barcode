# -*- coding: utf-8 -*-
# Copyright 2016-TODAY Janire Olagibel <janire.olagibel@factorlibre.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models


class ProductBarcodeMassAssignmentWizard(models.TransientModel):
    """ wizard for barcode """

    _name = "product.barcode.mass.assignment.wizard"
    _description = "Barcode Wizard for mass assignment"

    ean_sequence_id = fields.Many2one('ir.sequence', string='Ean sequence',
                                      required=True)

    @api.model
    def default_get(self, fields):
        """
        This function gets default values
        """
        res = super(ProductBarcodeMassAssignmentWizard, self).default_get(fields)
        user = self.env['res.users'].browse(self._uid)
        if user.company_id.ean_sequence_id:
            res.update({'ean_sequence_id': user.company_id.ean_sequence_id.id
                        if user.company_id.ean_sequence_id else False})
        return res

    @api.multi
    def do_assign(self):
        productobj = self.env['product.product']
        user = self.env['res.users'].browse(self._uid)

        products = productobj.search([
            ('id', 'in', self._context.get('active_ids', [])),
            ('company_id', '=', user.company_id.id)])
        if products:
            for product in products:
                if not product.ean13:
                    ean = self._get_ean_next_code()
                    if not ean:
                        continue
                    ean13 = ean + productobj._get_ean_control_digit(ean)
                    product.write({'ean13': ean13,
                                   'ean_sequence_id': self.ean_sequence_id.id})

    @api.model
    def _get_ean_next_code(self):
        sequence_obj = self.env['ir.sequence']
        exit = False
        while not exit:
            ean = sequence_obj.next_by_id(self.ean_sequence_id.id)
            ean = (len(ean[0:6]) == 6 and ean[0:6] or
                   ean[0:6].ljust(6, '0')) + ean[6:].rjust(6, '0')
            if len(ean) <= 12:
                exit = True
        return ean
