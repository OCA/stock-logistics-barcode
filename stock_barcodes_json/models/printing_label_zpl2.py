# Copyright (C) 2016 SYLEAM (<http://www.syleam.fr>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import api, fields, models
from odoo.tools.safe_eval import safe_eval

_logger = logging.getLogger(__name__)


class PrintingLabelZpl2(models.Model):
    _inherit = "printing.label.zpl2"

    data_type = fields.Selection(selection_add=[("json", "JSON")])

    @api.model
    def _get_component_data(self, component, eval_args):
        data = super()._get_component_data(component, eval_args)
        # TODO implement all types in zpl module
        if not self.env.context.get("ld", False):
            return data
        if component.component_type == "text" and not component.only_product_barcode:
            data = ""
            for _, val in self.env.context.get("ld", False).items():
                if isinstance(val, (str)):
                    data += str(val) + " | "
        elif component.component_type == "code_128" or component.only_product_barcode:
            data_copy = data.copy()
            for key, val in data_copy.items():
                if key == "product_barcode":
                    data = val
        else:
            data = self.env.context.get("ld", False)
        return data

    def print_label(self, printer, record, page_count=1, **extra):
        res = super().print_label(printer, record, page_count=1, **extra)
        for label in self:
            if label.data_type == "json":
                self.fill_component(self.env.context.get("mapping"))
                for component in self.component_ids:
                    data = safe_eval(component.data)
                    data_copy = data.copy()
                    info = ""
                    for key, val in data.items():
                        if not val:
                            data_copy.pop(key)
                            continue
                        if isinstance(val, models.BaseModel):
                            data_copy[key] = val.id
                        elif isinstance(val, list):
                            data_copy[key] = val[0]
                        elif isinstance(val, (int, float, str)):
                            data_copy[key] = val
                            info += "%s" % (val) + "\n"
                        else:
                            raise ValueError
                # Send the label to printer
                label_contents = label.with_context(ld=data_copy)._generate_zpl2_data(
                    self.env.context.get("mapping"), page_count=1, **extra
                )
                printer.print_document(
                    report=None, content=label_contents, doc_format="raw"
                )
        return res
