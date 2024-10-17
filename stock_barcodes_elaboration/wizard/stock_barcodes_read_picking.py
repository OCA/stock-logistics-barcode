# Copyright 2019 Sergio Teruel <sergio.teruel@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import models


class WizStockBarcodesReadPicking(models.TransientModel):
    _inherit = "wiz.stock.barcodes.read.picking"

    def _group_key(self, line):
        key = super()._group_key(line)
        if not self.option_group_id.group_key_for_todo_records:
            key += (str(line.elaboration_ids.ids),)
        return key

    def _prepare_fill_record_values(self, line, position):
        vals = super()._prepare_fill_record_values(line, position)
        vals["elaboration_ids"] = [(6, 0, line.elaboration_ids.ids)]
        vals["elaboration_note"] = ". ".join(
            m.elaboration_note for m in line if m.elaboration_note
        )
        return vals

    def _update_fill_record_values(self, line, vals):
        vals = super()._update_fill_record_values(line, vals)
        if not line.elaboration_ids:
            return vals
        elaboration_ids = vals.get("elaboration_ids", [(6, 0, [])])[2]
        for elaboration_id in line.elaboration_ids.ids:
            if elaboration_id not in elaboration_ids:
                elaboration_ids.append(elaboration_id)
            vals["elaboration_ids"] = elaboration_ids
        if (
            line.elaboration_note
            and line.elaboration_note not in vals["elaboration_note"]
        ):
            vals["elaboration_note"] += f". {line.elaboration_note}"
        return vals
