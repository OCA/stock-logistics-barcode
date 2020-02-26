# Copyright 2020 ForgeFlow S.L. (<http://www.forgeflow.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import models

_logger = logging.getLogger(__name__)


class PrintingLabelZpl2(models.Model):
    _inherit = "printing.label.zpl2"

    def _generate_zpl2_data(self, record, page_count=1, **extra):
        return super()._generate_zpl2_data(
            self.env.context.get("mapping", record), page_count, **extra
        )
