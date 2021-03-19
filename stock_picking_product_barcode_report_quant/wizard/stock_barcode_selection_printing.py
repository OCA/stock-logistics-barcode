# Copyright 2021 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models


class ProductPrintingQty(models.TransientModel):
    _inherit = "stock.picking.line.print"

    barcode = fields.Char(string="Barcode")

    def action_new_barcode(self):
        for line in self:
            line.barcode = self.env.ref(
                "stock_quant_barcode.sequence_quant_barcode"
            ).next_by_id()


class WizStockBarcodeSelectionPrinting(models.TransientModel):
    _inherit = "stock.picking.print"

    @api.model
    def _get_move_lines(self, picking):
        # Allow print lines although the product has not barcode
        if self.barcode_report != self.env.ref(
            "stock_picking_product_barcode_report_quant."
            "action_label_barcode_report_quant"
        ):
            return super()._get_move_lines(picking)
        return picking.move_line_ids

    @api.model
    def _prepare_data_from_move_line(self, move_line):
        res = super()._prepare_data_from_move_line(move_line)
        if move_line.barcode:
            res["barcode"] = move_line.barcode
        else:
            # Location denpends of move line state
            location = (
                move_line.location_dest_id
                if move_line.state == "done"
                else move_line.location_id
            )
            quant = self.env["stock.quant"]._gather(
                move_line.product_id,
                location,
                lot_id=move_line.lot_id,
                package_id=move_line.package_id,
                owner_id=move_line.owner_id,
                strict=True,
            )
            res["barcode"] = (
                quant.barcode
                or self.env.ref(
                    "stock_quant_barcode.sequence_quant_barcode"
                ).next_by_id()
            )
        return res

    def print_labels(self):
        Quant = self.env["stock.quant"]
        print_moves = self.product_print_moves.filtered(
            lambda p: p.label_qty > 0 and p.barcode
        )
        for print_move in print_moves:
            ml = print_move.move_line_id
            ml.barcode = print_move.barcode
            quant = Quant._gather(
                ml.product_id,
                ml.location_dest_id,
                lot_id=ml.lot_id,
                package_id=ml.package_id,
                owner_id=ml.owner_id,
                strict=True,
            )
            # TODO: Raise for more than one quant
            if not quant.barcode:
                quant.barcode = print_move.barcode
        return super().print_labels()

    def action_new_barcode_and_print(self):
        self.mapped("product_print_moves").action_new_barcode()
        return self.print_labels()
