# Copyright 2019 Sergio Teruel <sergio.teruel@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from collections import OrderedDict

from odoo import api, fields, models


class WizStockBarcodesReadTodo(models.TransientModel):
    _name = "wiz.stock.barcodes.read.todo"
    _description = "Wizard to read barcode todo"

    # To prevent remove the record wizard until 2 days old
    _transient_max_hours = 48

    name = fields.Char()
    wiz_barcode_id = fields.Many2one(comodel_name="wiz.stock.barcodes.read.picking")
    partner_id = fields.Many2one(
        comodel_name="res.partner", readonly=True, string="Partner",
    )
    state = fields.Selection(
        [("pending", "Pending"), ("done", "Done"), ("done_forced", "Done forced")],
        default="pending",
    )
    product_qty_reserved = fields.Float(
        "Reserved", digits="Product Unit of Measure", readonly=True,
    )
    product_uom_qty = fields.Float(
        "Demand", digits="Product Unit of Measure", readonly=True,
    )
    qty_done = fields.Float("Done", digits="Product Unit of Measure", readonly=True,)
    location_id = fields.Many2one(comodel_name="stock.location")
    location_dest_id = fields.Many2one(comodel_name="stock.location")
    product_id = fields.Many2one(comodel_name="product.product")
    lot_id = fields.Many2one(comodel_name="stock.production.lot")
    uom_id = fields.Many2one(comodel_name="uom.uom")

    res_model_id = fields.Many2one(comodel_name="ir.model")
    res_ids = fields.Char()
    line_ids = fields.Many2many(comodel_name="stock.move.line")

    def _group_key(self, line):
        return (line.location_id, line.product_id, line.lot_id)

    @api.model
    def fill_records(self, wiz_barcode, lines_list):
        """
        :param lines_list: browse list
        :return:
        """
        wiz_barcode.todo_line_ids.unlink()
        for lines in lines_list:
            todo_vals = OrderedDict()
            vals_list = []
            for line in lines:
                key = self._group_key(line)
                if key not in todo_vals:
                    todo_vals[key] = {
                        "location_id": line.location_id.id,
                        "location_dest_id": line.location_dest_id.id,
                        "product_id": line.product_id.id,
                        "lot_id": line.lot_id.id,
                        "uom_id": line.product_uom_id.id,
                        "product_qty_reserved": line.product_qty,
                        "product_uom_qty": line.product_uom_qty,
                        "qty_done": line.qty_done,
                        "line_ids": [(6, 0, line.ids)],
                        "name": "xxxx",
                    }
                else:
                    todo_vals[key]["product_qty_reserved"] += line.product_qty
                    todo_vals[key]["product_uom_qty"] += line.product_uom_qty
                    todo_vals[key]["qty_done"] += line.qty_done
                    todo_vals[key]["line_ids"][0][2].append(line.id)
                vals_list.append(todo_vals)
            # records = self.browse()
            # for vals in todo_vals.values():
            #     records += self.new(vals)
            # wiz_barcode.todo_line_ids = records
            wiz_barcode.todo_line_ids = self.create(list(todo_vals.values()))
