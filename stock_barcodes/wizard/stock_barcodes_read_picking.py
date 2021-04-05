# Copyright 2019 Sergio Teruel <sergio.teruel@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import logging

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.fields import first
from odoo.tools.float_utils import float_compare

_logger = logging.getLogger(__name__)


class WizStockBarcodesReadPicking(models.TransientModel):
    _name = "wiz.stock.barcodes.read.picking"
    _inherit = "wiz.stock.barcodes.read"
    _description = "Wizard to read barcode on picking"

    picking_id = fields.Many2one(
        comodel_name="stock.picking", string="Picking", readonly=True
    )
    candidate_picking_ids = fields.One2many(
        comodel_name="wiz.candidate.picking",
        inverse_name="wiz_barcode_id",
        string="Candidate pickings",
        readonly=True,
    )
    picking_product_qty = fields.Float(
        string="Picking quantities", digits="Product Unit of Measure", readonly=True
    )
    picking_type_code = fields.Selection(
        [("incoming", "Vendors"), ("outgoing", "Customers"), ("internal", "Internal")],
        "Type of Operation",
    )
    confirmed_moves = fields.Boolean(string="Confirmed moves")

    def name_get(self):
        return [
            (
                rec.id,
                "{} - {} - {}".format(
                    _("Barcode reader"),
                    rec.picking_id.name or rec.picking_type_code,
                    self.env.user.name,
                ),
            )
            for rec in self
        ]

    def _set_default_picking(self):
        picking_id = self.env.context.get("default_picking_id", False)
        if picking_id:
            self._set_candidate_pickings(self.env["stock.picking"].browse(picking_id))

    @api.model
    def create(self, vals):
        # When user click any view button the wizard record is create and the
        # picking candidates have been lost, so we need set it.
        wiz = super().create(vals)
        if wiz.picking_id:
            wiz._set_candidate_pickings(wiz.picking_id)
        return wiz

    @api.onchange("picking_id")
    def onchange_picking_id(self):
        # Add to candidate pickings the default picking. We are in a wizard
        # view, so for create a candidate picking with the same default picking
        # we need create it in this onchange
        self._set_default_picking()

    def action_done(self):
        if self.check_done_conditions():
            res = self._process_stock_move_line()
            if res:
                self._add_read_log(res)
                self.candidate_picking_ids.scan_count += 1

    def action_manual_entry(self):
        result = super().action_manual_entry()
        if result:
            self.action_done()
        return result

    def _prepare_move_line_values(self, candidate_move, available_qty):
        """When we've got an out picking, the logical workflow is that
        the scanned location is the location we're getting the stock
        from"""
        out_move = candidate_move.picking_code == "outgoing"
        location_id = self.location_id if out_move else self.picking_id.location_id
        location_dest_id = (
            self.picking_id.location_dest_id if out_move else self.location_id
        )
        return {
            "picking_id": self.picking_id.id,
            "move_id": candidate_move.id,
            "qty_done": available_qty,
            "product_uom_id": self.product_id.uom_po_id.id,
            "product_id": self.product_id.id,
            "location_id": location_id.id,
            "location_dest_id": location_dest_id.id,
            "lot_id": self.lot_id.id,
            "lot_name": self.lot_id.name,
        }

    def _states_move_allowed(self):
        move_states = ["assigned"]
        if self.confirmed_moves:
            move_states.append("confirmed")
        return move_states

    def _prepare_stock_moves_domain(self):
        domain = [
            ("product_id", "=", self.product_id.id),
            ("picking_id.picking_type_id.code", "=", self.picking_type_code),
            ("state", "in", self._states_move_allowed()),
        ]
        if self.picking_id:
            domain.append(("picking_id", "=", self.picking_id.id))
        return domain

    def _set_candidate_pickings(self, candidate_pickings):
        vals = [(5, 0, 0)]
        vals.extend([(0, 0, {"picking_id": p.id}) for p in candidate_pickings])
        self.candidate_picking_ids = vals

    def _search_candidate_pickings(self, moves_todo=False):
        if not moves_todo:
            moves_todo = self.env["stock.move"].search(
                self._prepare_stock_moves_domain()
            )
        if not self.picking_id:
            candidate_pickings = moves_todo.mapped("picking_id")
            candidate_pickings_count = len(candidate_pickings)
            if candidate_pickings_count > 1:
                self._set_candidate_pickings(candidate_pickings)
                return False
            if candidate_pickings_count == 1:
                self.picking_id = candidate_pickings
                self._set_candidate_pickings(candidate_pickings)
            _logger.info("No picking assigned")
        return True

    def _process_stock_move_line(self):
        """
        Search assigned or confirmed stock moves from a picking operation type
        or a picking. If there is more than one picking with demand from
        scanned product the interface allow to select what picking to work.
        If only there is one picking the scan data is assigned to it.
        """
        StockMove = self.env["stock.move"]
        StockMoveLine = self.env["stock.move.line"]
        moves_todo = StockMove.search(self._prepare_stock_moves_domain())
        if not self._search_candidate_pickings(moves_todo):
            return False
        lines = moves_todo.mapped("move_line_ids").filtered(
            lambda l: (
                l.picking_id == self.picking_id
                and l.product_id == self.product_id
                and l.lot_id == self.lot_id
            )
        )
        available_qty = self.product_qty
        move_lines_dic = {}
        for line in lines:
            if line.product_uom_qty:
                assigned_qty = min(
                    max(line.product_uom_qty - line.qty_done, 0.0), available_qty
                )
            else:
                assigned_qty = available_qty
            line.write({"qty_done": line.qty_done + assigned_qty})
            available_qty -= assigned_qty
            if assigned_qty:
                move_lines_dic[line.id] = assigned_qty
            if (
                float_compare(
                    available_qty,
                    0.0,
                    precision_rounding=line.product_id.uom_id.rounding,
                )
                < 1
            ):
                break
        if (
            float_compare(
                available_qty, 0, precision_rounding=self.product_id.uom_id.rounding
            )
            > 0
        ):
            # Create an extra stock move line if this product has an
            # initial demand.
            moves = self.picking_id.move_lines.filtered(
                lambda m: (
                    m.product_id == self.product_id
                    and m.state in self._states_move_allowed()
                )
            )
            if not moves:
                # TODO: Add picking if picking_id to message
                self._set_messagge_info(
                    "info", _("There are no stock moves to assign this operation")
                )
                return False
            else:
                line = StockMoveLine.create(
                    self._prepare_move_line_values(moves[0], available_qty)
                )
                move_lines_dic[line.id] = available_qty
        self.picking_product_qty = sum(moves_todo.mapped("quantity_done"))
        return move_lines_dic

    def _candidate_picking_selected(self):
        if len(self.candidate_picking_ids) == 1:
            return self.candidate_picking_ids.picking_id
        else:
            return self.env["stock.picking"].browse()

    def check_done_conditions(self):
        res = super().check_done_conditions()
        if self.product_id.tracking != "none" and not self.lot_id:
            self._set_messagge_info("info", _("Waiting for input lot"))
            return False
        if not self.picking_id:
            if not self._search_candidate_pickings():
                self._set_messagge_info(
                    "info", _("Click on picking pushpin to lock it")
                )
                return False
        if self.picking_id != self._candidate_picking_selected():
            self._set_messagge_info("info", _("Click on picking pushpin to lock it"))
            return False
        return res

    def _prepare_scan_log_values(self, log_detail=False):
        # Store in read log line each line added with the quantities assigned
        vals = super()._prepare_scan_log_values(log_detail=log_detail)
        vals["picking_id"] = self.picking_id.id
        if log_detail:
            vals["log_line_ids"] = [
                (0, 0, {"move_line_id": x[0], "product_qty": x[1]})
                for x in log_detail.items()
            ]
        return vals

    def remove_scanning_log(self, scanning_log):
        for log in scanning_log:
            for log_scan_line in log.log_line_ids:
                if log_scan_line.move_line_id.state not in ["assigned", "confirmed"]:
                    raise ValidationError(
                        _(
                            "You can not remove an entry linked to a stock move "
                            "line in state assigned or confirmed"
                        )
                    )
                qty = log_scan_line.move_line_id.qty_done - log_scan_line.product_qty
                log_scan_line.move_line_id.qty_done = max(qty, 0.0)
            self.picking_product_qty = sum(
                log.log_line_ids.mapped("move_line_id.move_id.quantity_done")
            )
            log.unlink()

    def action_undo_last_scan(self):
        res = super().action_undo_last_scan()
        log_scan = first(
            self.scan_log_ids.filtered(lambda x: x.create_uid == self.env.user)
        )
        self.remove_scanning_log(log_scan)
        return res


class WizCandidatePicking(models.TransientModel):
    """
    TODO: explain
    """

    _name = "wiz.candidate.picking"
    _description = "Candidate pickings for barcode interface"
    # To prevent remove the record wizard until 2 days old
    _transient_max_hours = 48

    wiz_barcode_id = fields.Many2one(
        comodel_name="wiz.stock.barcodes.read.picking", readonly=True
    )
    picking_id = fields.Many2one(
        comodel_name="stock.picking", string="Picking", readonly=True
    )
    wiz_picking_id = fields.Many2one(
        comodel_name="stock.picking",
        related="wiz_barcode_id.picking_id",
        string="Wizard Picking",
        readonly=True,
    )
    name = fields.Char(
        related="picking_id.name", readonly=True, string="Candidate Picking"
    )
    partner_id = fields.Many2one(
        comodel_name="res.partner",
        related="picking_id.partner_id",
        readonly=True,
        string="Partner",
    )
    state = fields.Selection(related="picking_id.state", readonly=True)
    date = fields.Datetime(
        related="picking_id.date", readonly=True, string="Creation Date"
    )
    product_qty_reserved = fields.Float(
        "Reserved",
        compute="_compute_picking_quantity",
        digits="Product Unit of Measure",
        readonly=True,
    )
    product_uom_qty = fields.Float(
        "Demand",
        compute="_compute_picking_quantity",
        digits="Product Unit of Measure",
        readonly=True,
    )
    product_qty_done = fields.Float(
        "Done",
        compute="_compute_picking_quantity",
        digits="Product Unit of Measure",
        readonly=True,
    )
    # For reload kanban view
    scan_count = fields.Integer()

    @api.depends("scan_count")
    def _compute_picking_quantity(self):
        for candidate in self:
            qty_reserved = 0
            qty_demand = 0
            qty_done = 0
            candidate.product_qty_reserved = sum(
                candidate.picking_id.mapped("move_lines.reserved_availability")
            )
            for move in candidate.picking_id.move_lines:
                qty_reserved += move.reserved_availability
                qty_demand += move.product_uom_qty
                qty_done += move.quantity_done
            candidate.update(
                {
                    "product_qty_reserved": qty_reserved,
                    "product_uom_qty": qty_demand,
                    "product_qty_done": qty_done,
                }
            )

    def _get_wizard_barcode_read(self):
        return self.env["wiz.stock.barcodes.read.picking"].browse(
            self.env.context["wiz_barcode_id"]
        )

    def action_lock_picking(self):
        wiz = self._get_wizard_barcode_read()
        picking_id = self.env.context["picking_id"]
        wiz.picking_id = picking_id
        wiz._set_candidate_pickings(wiz.picking_id)
        return wiz.action_done()

    def action_unlock_picking(self):
        wiz = self._get_wizard_barcode_read()
        wiz.update(
            {
                "picking_id": False,
                "candidate_picking_ids": False,
                "message_type": False,
                "message": False,
            }
        )
        return wiz.action_cancel()

    def action_validate_picking(self):
        picking = self.env["stock.picking"].browse(
            self.env.context.get("picking_id", False)
        )
        return picking.button_validate()
