# Copyright 2020 ForgeFlow S.L. (<http://www.forgeflow.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models

from ..wizard.print_record_label import _supported_models


class PrintingLabelZpl2Component(models.Model):
    _inherit = "printing.label.zpl2.component"

    def process_model(self, model):
        if model.model in _supported_models:
            return self.env["ir.model"]._get("wizard.print.record.label.line")
        return model

    @api.model
    def autofill_data(self, record, eval_args):
        if record._name == "wizard.print.record.label.line":
            return {
                "product_barcode": record.product_barcode,
                "lot_barcode": record.lot_barcode,
                "uom_id": record.product_id.uom_id.id,
                "package_barcode": record.package_barcode,
                "product_qty": record.product_qty,
            }
        else:
            return super().autofill_data(record, eval_args)
