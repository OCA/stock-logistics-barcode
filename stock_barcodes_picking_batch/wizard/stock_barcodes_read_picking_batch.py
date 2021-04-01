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
    candidate_picking_batch_ids = fields.One2many(
        comodel_name="wiz.candidate.picking.batch",
        inverse_name="wiz_barcode_id",
        string="Candidate picking batch",
        readonly=True,
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
        selection_add=[("picking_batch", "Picking batch mode")]
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

    def _set_default_picking_batch(self):
        picking_batch_id = self.env.context.get("default_picking_batch_id", False)
        if picking_batch_id:
            self._set_candidate_picking_batchs(
                self.env["stock.picking.batch"].browse(picking_batch_id)
            )

    @api.model
    def create(self, vals):
        # When user click any view button the wizard record is create and the
        # picking batch candidates have been lost, so we need set it.
        wiz = super().create(vals)
        if wiz.picking_batch_id:
            wiz._set_candidate_picking_batchs(wiz.picking_batch_id)
        return wiz

    @api.onchange("picking_batch_id")
    def onchange_picking_batch_id(self):
        # Add to candidate picking batchs the default picking batch.
        # We are in a wizard view, so for create a candidate picking batch
        # with the same default picking batch we need create it in this onchange
        self._set_default_picking_batch()
        self.determine_todo_action()

    def get_sorted_move_lines(self, move_lines):
        if self.picking_mode != "picking_batch":
            return super().get_sorted_move_lines(move_lines)
        if self.picking_batch_id.picking_ids[:1].picking_type_code in [
            "incoming",
            "internal",
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

    def _get_stock_move_lines_todo(self):
        move_lines = self.picking_batch_id.move_line_ids.filtered(
            lambda ml: (not ml.barcode_scan_state or ml.barcode_scan_state == "pending")
            and ml.qty_done < ml.product_qty
        )
        return move_lines

    def get_moves_or_move_lines(self):
        if self.picking_mode != "picking_batch":
            return super().get_moves_or_move_lines()
        if self.option_group_id.source_pending_moves == "move_line_ids":
            return self.picking_batch_id.move_line_ids.filtered(lambda ln: ln.move_id)
        else:
            return self.picking_batch_id.move_lines

    def update_fields_after_determine_todo(self, move_line):
        self.picking_batch_product_qty = move_line.qty_done

    def _prepare_stock_moves_domain(self):
        domain = super()._prepare_stock_moves_domain()
        if self.picking_batch_id:
            domain.append(("picking_id", "in", self.picking_batch_id.picking_ids.ids))
        return domain

    def _set_candidate_picking_batchs(self, candidate_picking_batchs):
        vals = [(5, 0, 0)]
        vals.extend(
            [(0, 0, {"picking_batch_id": p.id}) for p in candidate_picking_batchs]
        )
        self.candidate_picking_batch_ids = vals

    def _search_candidate_picking_batch(self, moves_todo=False):
        if not moves_todo:
            moves_todo = self.env["stock.move"].search(
                self._prepare_stock_moves_domain()
            )
        if not self.picking_batch_id:
            candidate_picking_batchs = moves_todo.mapped("picking_id.batch_id")
            candidate_picking_batch_count = len(candidate_picking_batchs)
            if candidate_picking_batch_count > 1:
                self._set_candidate_picking_batchs(candidate_picking_batchs)
                return False
            if candidate_picking_batch_count == 1:
                self.picking_batch_id = candidate_picking_batchs
                self._set_candidate_picking_batchs(candidate_picking_batchs)
            _logger.info("No picking batch assigned")
        return True

    def update_fields_after_process_stock(self, moves):
        if self.picking_mode != "picking_batch":
            return super().update_fields_after_process_stock(moves)
        self.picking_batch_product_qty = sum(moves.mapped("quantity_done"))

    def _candidate_picking_batch_selected(self):
        if len(self.candidate_picking_batch_ids) == 1:
            return self.candidate_picking_batch_ids.picking_batch_id
        else:
            return self.env["stock.picking.batch"].browse()

    def check_done_conditions(self):
        res = super().check_done_conditions()
        if self.picking_mode != "picking_batch":
            return res
        if not self.picking_batch_id:
            if not self._search_candidate_picking_batch():
                self._set_messagge_info(
                    "info", _("Click on picking batch pushpin to lock it")
                )
                return False
        if (
            self.picking_batch_id
            and self.picking_batch_id != self._candidate_picking_batch_selected()
        ):
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
                        "stock_barcodes_picking_batch."
                        "view_stock_barcodes_read_picking_batch_form"
                    ).id,
                    "form",
                )
            ]
        return action

    # def _prepare_move_line_values(self, candidate_move, available_qty):
    #     """ When an extra stock move line is created for a batch picking we
    #         must apply a strategy that allows find what picking will receive
    #         this new line.
    #     """
    #     if self.picking_mode != "picking_batch":
    #         return super()._prepare_move_line_values(candidate_move, available_qty)
    #     to_do = self.todo_line_ids.filtered(
    #         lambda ln:
    #             ln.barcode_scan_state == 'pending' and
    #             ln.product_id == self.product_id and
    #             ln.qty_done < ln.product_uom_qty
    #     )

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
        # TODO: split beetwen all lines
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
        return sml
        # if moves:
        #     myself = self.with_context(picking=moves[:1].picking_id)
        # else:
        #     myself = self
        # return super(
        # WizStockBarcodesReadPickingBatch, myself
        # ).create_new_stock_move_line(moves_todo, available_qty)


class WizCandidatePickingBatch(models.TransientModel):
    """
    TODO: explain
    """

    _name = "wiz.candidate.picking.batch"
    _description = "Candidate picking batchs for barcode interface"

    # To prevent remove the record wizard until 2 days old
    _transient_max_hours = 48

    wiz_barcode_id = fields.Many2one(
        comodel_name="wiz.stock.barcodes.read.picking", readonly=True
    )
    picking_batch_id = fields.Many2one(
        comodel_name="stock.picking.batch", string="Picking batch", readonly=True
    )
    wiz_picking_batch_id = fields.Many2one(
        comodel_name="stock.picking.batch",
        related="wiz_barcode_id.picking_batch_id",
        string="Wizard Picking Batch",
        readonly=True,
    )
    name = fields.Char(
        related="picking_batch_id.name", readonly=True, string="Candidate Picking Batch"
    )
    state = fields.Selection(related="picking_batch_id.state", readonly=True)
    date = fields.Datetime(
        related="picking_batch_id.create_date", readonly=True, string="Creation Date"
    )
    product_ref_count = fields.Integer(
        compute="_compute_product_ref_count", string="#Product Ref:"
    )
    product_ref_done = fields.Integer(
        compute="_compute_product_ref_count", string="#Product Ref done:"
    )
    # For reload kanban view
    scan_count = fields.Integer()
    is_pending = fields.Boolean(compute="_compute_is_pending")

    @api.depends("scan_count")
    def _compute_product_ref_count(self):
        for candidate in self:
            bp_products = set(
                candidate.picking_batch_id.move_lines.mapped("product_id")
            )
            bp_products_pending = set(
                candidate.picking_batch_id.move_lines.filtered(
                    lambda ln: ln.quantity_done < ln.product_uom_qty
                ).mapped("product_id")
            )
            candidate.update(
                {
                    "product_ref_count": len(bp_products),
                    "product_ref_done": len(bp_products - bp_products_pending),
                }
            )

    @api.depends("scan_count")
    def _compute_is_pending(self):
        for rec in self:
            rec.is_pending = bool(
                rec.picking_batch_id.move_line_ids.filtered(
                    lambda ln: ln.barcode_scan_state == "pending"
                )
            )

    def _get_wizard_barcode_read(self):
        return self.env["wiz.stock.barcodes.read.picking"].browse(
            self.env.context["wiz_barcode_id"]
        )

    def action_lock_picking(self):
        wiz = self._get_wizard_barcode_read()
        picking_id = self.env.context["picking_id"]
        wiz.picking_id = picking_id
        wiz._set_candidate_picking_batchs(wiz.picking_id)
        return wiz.action_done()

    def action_unlock_picking_batch(self):
        wiz = self._get_wizard_barcode_read()
        wiz.update(
            {
                "picking_batch_id": False,
                "candidate_picking_batch_ids": False,
                "message_type": False,
                "message": False,
            }
        )
        return wiz.action_cancel()

    def action_validate_picking_batch(self):
        picking_batch = self.env["stock.picking.batch"].browse(
            self.env.context.get("picking_batch_id", False)
        )
        picking_batch.action_transfer()
        return self.env.ref("stock_barcodes.action_stock_barcodes_action").read()[0]

    def action_open_picking_batch(self):
        picking_batch = self.env["stock.picking.batch"].browse(
            self.env.context.get("picking_batch_id", False)
        )
        return picking_batch.get_formview_action()
