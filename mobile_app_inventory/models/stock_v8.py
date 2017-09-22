# -*- coding: utf-8 -*-

from openerp import api, models, fields, _
from openerp import exceptions

class StockInventory(models.Model):
    _inherit = 'stock.inventory'
    print "ici !!"

    @api.model
    def add_inventory_line_by_scan(self,args):
        print "do something"