# Copyright 2019 Sergio Teruel <sergio.teruel@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import logging

from odoo import _, api, fields, models
from odoo.tools.float_utils import float_compare

_logger = logging.getLogger(__name__)


class WizStockBarcodesReadPickingBatch(models.TransientModel):
    _inherit = "wiz.stock.barcodes.read.picking"
    _description = "Wizard to read barcode on picking batch"

    picking_batch_id = fields.Many2one(
        comodel_name="stock.picking.batch", string="Picking Batch", readonly=True
    )
    # TODO: Remove this field
    picking_batch_product_qty = fields.Float(
        string="Picking batch quantities",
        digits="Product Unit of Measure",
        readonly=True,
    )
    picking_type_code = fields.Selection(
        [("incoming", "Vendors"), ("outgoing", "Customers"), ("internal", "Internal")],
        "Type of Operation",
    )
    confirmed_moves = fields.Boolean(string="Confirmed moves")
    picking_mode = fields.Selection(
        selection_add=[("picking_batch", "Picking batch mode")],
        ondelete={"picking_batch": "set picking"},
    )
    picking_batch_state = fields.Selection(related="picking_batch_id.state")
    picking_batch_show_validate = fields.Boolean(
        related="picking_batch_id.show_validate"
    )
    picking_batch_show_check_availability = fields.Boolean(
        related="picking_batch_id.show_check_availability"
    )

    def name_get(self):
        if self.picking_mode != "picking_batch":
            return super().name_get()
        return [
            (
                rec.id,
                "{} - {} - {}".format(
                    _("Barcode reader"),
                    rec.picking_batch_id.name or rec.picking_type_code,
                    self.env.user.name,
                ),
            )
            for rec in self
        ]

    def _compute_move_line_ids(self):
        if self.picking_mode != "picking_batch":
            return super(
                WizStockBarcodesReadPickingBatch, self
            )._compute_move_line_ids()
        self.move_line_ids = self.picking_batch_id.move_line_ids.filtered(
            "qty_done"
        ).sorted("write_date", reverse=True)

    @api.onchange("picking_batch_id")
    def onchange_picking_batch_id(self):
        self.fill_pending_moves()
        self.determine_todo_action()

    def get_sorted_move_lines(self, move_lines):
        if self.picking_mode != "picking_batch":
            return super().get_sorted_move_lines(move_lines)
        if self.picking_batch_id.picking_ids[:1].picking_type_code in [
            "incoming",
        ]:
            location_field = "location_dest_id"
        else:
            location_field = "location_id"
        move_lines = move_lines.sorted(
            lambda ml: (
                ml[location_field].posx,
                ml[location_field].posy,
                ml[location_field].posz,
                ml[location_field].name,
            )
        )
        return move_lines

    def get_moves_or_move_lines(self):
        if self.picking_mode != "picking_batch":
            return super().get_moves_or_move_lines()
        if self.option_group_id.source_pending_moves == "move_line_ids":
            return self.picking_batch_id.move_line_ids.filtered(lambda ln: ln.move_id)
        else:
            return self.picking_batch_id.move_ids

    def update_fields_after_determine_todo(self, move_line):
        if self.picking_mode != "picking_batch":
            return super().update_fields_after_determine_todo(move_line)
        self.picking_batch_product_qty = move_line.qty_done

    def _prepare_stock_moves_domain(self):
        domain = super()._prepare_stock_moves_domain()
        if self.picking_batch_id:
            domain.append(("picking_id", "in", self.picking_batch_id.picking_ids.ids))
        return domain

    def update_fields_after_process_stock(self, moves):
        if self.picking_mode != "picking_batch":
            return super().update_fields_after_process_stock(moves)
        self.picking_batch_product_qty = sum(moves.mapped("quantity_done"))

    def check_done_conditions(self):
        res = super().check_done_conditions()
        if self.picking_mode != "picking_batch":
            return res
        if not self.picking_batch_id:
            self._set_messagge_info(
                "info", _("Click on picking batch pushpin to lock it")
            )
            return False
        return res

    def action_back(self):
        action = super().action_back()
        if self.picking_mode == "picking_batch":
            action["views"] = [
                (
                    self.env.ref(
                        "stock_barcodes_picking_batch.stock_batch_picking_form"
                    ).id,
                    "form",
                )
            ]
        return action

    def create_new_stock_move_line(self, moves_todo, available_qty):
        if self.picking_mode != "picking_batch" or self.env.context.get(
            "skip_split_quantity_between_moves", False
        ):
            return super().create_new_stock_move_line(moves_todo, available_qty)
        to_do = self.todo_line_ids.filtered(
            lambda ln: ln.state == "pending"
            and ln.product_id == self.product_id
            and ln.qty_done < ln.product_uom_qty
        )
        if to_do.line_ids:
            moves = to_do.line_ids.filtered(
                lambda ln: ln.barcode_scan_state == "pending"
            )
        else:
            moves = to_do.stock_move_ids.filtered(
                lambda ln: ln.ln.quantity_done < ln.product_uom_qty
            )
        # TODO: split between all lines
        sml = self.env["stock.move.line"].browse()
        for move in moves:
            move_qty_done = (
                "qty_done" if move._name == "stock.move.line" else "quantity_done"
            )
            if move.product_uom_qty:
                assigned_qty = min(
                    max(move.product_uom_qty - move[move_qty_done], 0.0), available_qty
                )
            else:
                assigned_qty = available_qty
            available_qty -= assigned_qty
            if move == moves[-1:] and (
                float_compare(
                    available_qty, 0, precision_rounding=self.product_id.uom_id.rounding
                )
                > 0
            ):
                # Assig all to last move
                assigned_qty += available_qty
            sml += self.env["stock.move.line"].create(
                self.with_context(picking=move.picking_id)._prepare_move_line_values(
                    move.move_id if move._name == "stock.move.line" else move,
                    assigned_qty,
                )
            )
        if available_qty:
            # What do I do with the extra quantities?
            # By moment I assign all to the last picking
            last_move = self.picking_batch_id.move_ids.filtered(
                lambda mv: mv.product_id == self.product_id
            )[-1]
            sml += self.env["stock.move.line"].create(
                self.with_context(
                    picking=last_move.picking_id
                )._prepare_move_line_values(
                    last_move,
                    available_qty,
                )
            )
        return sml

    def action_open_picking_batch(self):
        return self.picking_batch_id.get_formview_action()

    def action_validate_picking_batch(self):
        res = self.picking_batch_id.action_done()
        if res:
            return self.env["ir.actions.actions"]._for_xml_id(
                "stock_barcodes.action_stock_barcodes_action"
            )
        return res
