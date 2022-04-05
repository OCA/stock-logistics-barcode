# Copyright 2108-2019 Sergio Teruel <sergio.teruel@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class WizStockBarcodesReadTester(models.TransientModel):
    _name = "wiz.stock.barcodes.read.tester"
    _description = "Wizard to read barcode Tester"
    _inherit = ["wiz.stock.barcodes.read"]
