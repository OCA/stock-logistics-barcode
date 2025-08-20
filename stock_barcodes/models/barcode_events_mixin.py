# Copyright 2019 Sergio Teruel <sergio.teruel@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class BarcodesEventsMixin(models.AbstractModel):
    _inherit = "barcodes.barcode_events_mixin"

    def send_bus_done(self, channel, type_channel, data=None):
        self.env["bus.bus"]._sendone(channel, type_channel, data or {})
