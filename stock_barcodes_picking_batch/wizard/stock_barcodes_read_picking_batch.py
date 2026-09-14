# Copyright 2019 Sergio Teruel <sergio.teruel@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import logging

from odoo import _, api, fields, models

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
    picking_batch_show_check_availability = fields.Boolean(
        related="picking_batch_id.show_check_availability"
    )
    # In batch mode picking_id is empty, so take these values from the batch
    picking_location_id = fields.Many2one(
        comodel_name="stock.location",
        related=False,
        compute="_compute_picking_locations",
    )
    picking_location_dest_id = fields.Many2one(
        comodel_name="stock.location",
        related=False,
        compute="_compute_picking_locations",
    )
    company_id = fields.Many2one(
        comodel_name="res.company", related=False, compute="_compute_company_id"
    )

    @api.depends(
        "picking_mode",
        "picking_id.location_id",
        "picking_id.location_dest_id",
        "picking_batch_id.picking_ids.location_id",
        "picking_batch_id.picking_ids.location_dest_id",
    )
    def _compute_picking_locations(self):
        for rec in self:
            picking = rec.picking_id
            if rec.picking_mode == "picking_batch":
                picking = rec.picking_batch_id.picking_ids[:1]
            rec.picking_location_id = picking.location_id
            rec.picking_location_dest_id = picking.location_dest_id

    @api.depends("picking_mode", "picking_id.company_id", "picking_batch_id.company_id")
    def _compute_company_id(self):
        for rec in self:
            if rec.picking_mode == "picking_batch":
                rec.company_id = rec.picking_batch_id.company_id
            else:
                rec.company_id = rec.picking_id.company_id

    @api.depends("picking_batch_id", "picking_type_code", "picking_mode")
    def _compute_display_name(self):
        # v18: name_get was removed; display_name is computed. Keep the
        # "Barcode reader - <batch/type> - <user>" label for batch wizards
        # and delegate the rest to the base implementation.
        batch_recs = self.filtered(lambda r: r.picking_mode == "picking_batch")
        for rec in batch_recs:
            rec.display_name = "{} - {} - {}".format(
                _("Barcode reader"),
                rec.picking_batch_id.name or rec.picking_type_code,
                self.env.user.name,
            )
        other = self - batch_recs
        if other:
            return super(
                WizStockBarcodesReadPickingBatch, other
            )._compute_display_name()
        return None

    @api.depends("picking_mode", "picking_batch_id.move_line_ids.qty_picked")
    def _compute_move_line_ids(self):
        for wizard in self:
            if wizard.picking_mode != "picking_batch":
                super(WizStockBarcodesReadPickingBatch, wizard)._compute_move_line_ids()
            else:
                wizard.move_line_ids = wizard.picking_batch_id.move_line_ids.filtered(
                    "qty_picked"
                ).sorted("write_date", reverse=True)
        return None

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
                ml[location_field].complete_name,
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

    def get_moves(self):
        if self.picking_mode == "picking_batch":
            return self.picking_batch_id.move_ids
        return super().get_moves()

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
        uom = self.product_uom_id or self.product_id.uom_id
        self.picking_batch_product_qty = sum(
            move.product_uom._compute_quantity(move.quantity, uom, round=False)
            for move in moves
        )

    def check_done_conditions(self):
        res = super().check_done_conditions()
        if self.picking_mode != "picking_batch":
            return res
        if not self.picking_batch_id:
            self._set_message_info(
                "info", _("Click on picking batch pushpin to lock it")
            )
            return False
        return res

    def action_back(self):
        """Compatibility entry point for clients using the former back button."""
        if self.picking_mode == "picking_batch":
            return self.action_open_picking_batch()
        return self.action_open_picking()

    def create_new_stock_move_line(self, moves_todo, available_qty):
        if self.picking_mode != "picking_batch" or self.env.context.get(
            "skip_split_quantity_between_moves", False
        ):
            return super().create_new_stock_move_line(moves_todo, available_qty)
        candidate = moves_todo[:1]
        picking = (
            candidate.picking_id
            or self.picking_batch_id.picking_ids.filtered(
                lambda record: record.state not in ("done", "cancel")
            )[-1:]
        )
        return super(
            WizStockBarcodesReadPickingBatch, self.with_context(picking=picking)
        ).create_new_stock_move_line(moves_todo, available_qty)

    def action_open_picking_batch(self):
        return self.picking_batch_id.get_formview_action()

    def action_validate_picking_batch(self):
        self.picking_batch_id.picking_ids.filtered(
            lambda picking: picking.state not in ("done", "cancel")
        ).set_quantity_from_picked()
        res = self.picking_batch_id.with_context(
            stock_barcodes_read_picking_id=self.id
        ).action_done()
        return res

    def _get_moves_from_product_domain(self):
        domain = super()._get_moves_from_product_domain()
        if self.picking_mode == "picking_batch":
            domain.append(("id", "in", self.picking_batch_id.move_ids.ids))
        return domain

    def get_action_after_validate(self):
        if self.picking_batch_id:
            if self.picking_batch_id.state == "done":
                # Return to batches list
                return self.picking_batch_id.picking_type_id.action_batch()
            if self.picking_mode != "picking_batch":
                self.picking_mode = "picking_batch"
                self.picking_id = False
                self.res_model_id = self.env.ref(
                    "stock_picking_batch.model_stock_picking_batch"
                ).id
                self.res_id = self.picking_batch_id.id
            return self.picking_batch_id.action_barcode_scan(wiz=self)
        return super().get_action_after_validate()

    def _get_location_domain_for_quant_search(self):
        if self.picking_mode == "picking_batch" and self.picking_batch_id:
            location_ids = self.picking_batch_id.picking_ids.mapped("location_id")
            return [("location_id", "child_of", location_ids.ids)]
        return super()._get_location_domain_for_quant_search()
