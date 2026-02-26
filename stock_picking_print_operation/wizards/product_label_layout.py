# Copyright 2026 ACSONE SA/NV
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
from collections import defaultdict

from odoo import fields, models


class ProductLabelLayout(models.TransientModel):
    _inherit = "product.label.layout"

    move_line_ids = fields.Many2many(
        comodel_name="stock.move.line",
    )
    move_quantity = fields.Selection(
        selection_add=[("line", "Detailed Operation Quantities")],
        ondelete={"line": "set default"},
    )

    def _prepare_report_data(self):
        xml_id, data = super()._prepare_report_data()

        quantities = defaultdict(int)
        uom_unit = self.env.ref("uom.product_uom_categ_unit", raise_if_not_found=False)
        if self.move_quantity == "line" and self.move_line_ids:
            custom_barcodes = defaultdict(list)
            for line in self.move_line_ids:
                if line.product_uom_id.category_id == uom_unit:
                    if (line.lot_id or line.lot_name) and int(line.quantity):
                        custom_barcodes[line.product_id.id].append(
                            (line.lot_id.name or line.lot_name, int(line.quantity))
                        )
                        continue
                    quantities[line.product_id.id] += int(line.quantity)
                else:
                    quantities[line.product_id.id] = 1
            # Pass only products with some quantity done to the report
            data["quantity_by_product"] = {
                p: int(q) for p, q in quantities.items() if q
            }
            data["custom_barcodes"] = custom_barcodes

        return xml_id, data
