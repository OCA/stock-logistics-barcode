# Copyright (C) 2011 Julius Network Solutions SARL <contact@julius.fr>
# Copyright 2018 Camptocamp SA
# Copyright 2019 Sergio Teruel - Tecnativa <sergio.teruel@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models, _


class StockMoveLocationWizard(models.TransientModel):
    _inherit = "wiz.stock.move.location"

    def name_get(self):
        return [
            (rec.id, '{} - {}'.format(
                _('Move Between Locations'),
                self.env.user.name)) for rec in self]

    def action_barcode_scan(self):
        action = self.env.ref(
            'stock_barcodes_move_location.'
            'action_stock_barcodes_read_stock_move_location').read()[0]
        action['context'] = {
            'default_location_id': self.destination_location_id.id,
            'default_move_location_id': self.id,
            'default_res_model_id':
                self.env.ref(
                    'stock_move_location.model_wiz_stock_move_location').id,
            'default_res_id': self.id,
        }
        return action

    def clear_lines(self):
        self._clear_lines()
