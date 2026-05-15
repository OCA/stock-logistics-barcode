# Copyright 2019 Sergio Teruel <sergio.teruel@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import logging
from collections import OrderedDict, defaultdict

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.fields import first
from odoo.tools.float_utils import float_compare, float_round
from odoo.tools.safe_eval import safe_eval

_logger = logging.getLogger(__name__)


class WizStockBarcodesReadPicking(models.TransientModel):
    _name = "wiz.stock.barcodes.read.picking"
    _inherit = "wiz.stock.barcodes.read"
    _description = "Wizard to read barcode on picking"

    picking_id = fields.Many2one(
        comodel_name="stock.picking", string="Picking", readonly=True
    )
    picking_state = fields.Selection(related="picking_id.state")
    picking_ids = fields.Many2many(
        comodel_name="stock.picking", string="Pickings", readonly=True
    )
    picking_product_qty = fields.Float(
        string="Picking quantities", digits="Product Unit of Measure", readonly=True
    )
    picking_type_code = fields.Selection(
        [("incoming", "Vendors"), ("outgoing", "Customers"), ("internal", "Internal")],
        "Type of Operation",
    )
    # Restored from 16.0 — the wizard exposes a one2many to wiz.candidate.picking
    # so the form can list and lock/unlock candidate pickings while scanning.
    candidate_picking_ids = fields.One2many(
        comodel_name="wiz.candidate.picking",
        inverse_name="wiz_barcode_id",
        string="Candidate pickings",
        readonly=True,
    )

    move_line_ids = fields.One2many(
        comodel_name="stock.move.line", compute="_compute_move_line_ids"
    )
    todo_line_ids = fields.One2many(
        string="To Do Lines",
        comodel_name="wiz.stock.barcodes.read.todo",
        inverse_name="wiz_barcode_id",
    )
    todo_line_display_ids = fields.Many2many(
        comodel_name="wiz.stock.barcodes.read.todo",
        compute="_compute_todo_line_display_ids",
    )
    todo_line_id = fields.Many2one(comodel_name="wiz.stock.barcodes.read.todo")
    picking_mode = fields.Selection([("picking", "Picking mode")])
    pending_move_ids = fields.Many2many(
        comodel_name="wiz.stock.barcodes.read.todo",
        compute="_compute_pending_move_ids",
    )
    selected_pending_move_id = fields.Many2one(
        comodel_name="wiz.stock.barcodes.read.todo"
    )
    show_detailed_operations = fields.Boolean(
        related="option_group_id.show_detailed_operations", store=True
    )
    keep_screen_values = fields.Boolean(related="option_group_id.keep_screen_values")
    # Extended from stock_barcodes_read base model
    total_product_uom_qty = fields.Float(compute="_compute_total_product")
    total_product_qty_done = fields.Float(compute="_compute_total_product")
    # Technical fields to compute locations domain based on picking location
    picking_location_id = fields.Many2one(related="picking_id.location_id")
    picking_location_dest_id = fields.Many2one(related="picking_id.location_dest_id")
    company_id = fields.Many2one(related="picking_id.company_id")
    todo_line_is_extra_line = fields.Boolean(related="todo_line_id.is_extra_line")
    forced_todo_key = fields.Char()
    qty_available = fields.Float(compute="_compute_qty_available")
    partner_id = fields.Many2one("res.partner", related="picking_id.partner_id")
    partner_name = fields.Char(related="partner_id.name")
    enable_add_product = fields.Boolean(compute="_compute_enable_add_product")

    def action_show_detailed_operations(self):
        self.show_detailed_operations = not self.show_detailed_operations

    @api.depends("picking_state")
    def _compute_enable_add_product(self):
        for rec in self:
            rec.enable_add_product = rec.picking_state != "done"

    @api.depends("todo_line_id")
    def _compute_todo_line_display_ids(self):
        """Technical field to display only the first record in kanban view"""
        self.todo_line_display_ids = self.todo_line_id

    @api.depends("todo_line_ids", "picking_id.move_line_ids.qty_picked")
    def _compute_pending_move_ids(self):
        if self.option_group_id.show_pending_moves == "pending":
            self.pending_move_ids = self.todo_line_ids.filtered(
                lambda t: t.state == "pending"
                and any(
                    sm.barcode_backorder_action == "pending" for sm in t.stock_move_ids
                )
            )
        elif self.option_group_id.show_pending_moves == "all":
            self.pending_move_ids = self.todo_line_ids.filtered(
                lambda t: not t.is_extra_line
            )
        else:
            self.pending_move_ids = False

    @api.depends(
        "todo_line_ids", "todo_line_ids.qty_done", "picking_id.move_line_ids.qty_picked"
    )
    def _compute_move_line_ids(self):
        self.move_line_ids = self.picking_id.move_line_ids.filtered(
            "qty_picked"
        ).sorted(key=lambda sml: (sml.write_date, sml.create_date), reverse=True)

    @api.depends("picking_id.move_line_ids.qty_picked")
    def _compute_total_product(self):
        self.total_product_uom_qty = 0.0
        self.total_product_qty_done = 0.0
        for rec in self:
            product_moves = rec.picking_id.move_ids.filtered(
                lambda ln: ln.product_id.ids == self.product_id.ids
                and ln.state != "cancel"
            )
            for line in product_moves:
                rec.total_product_uom_qty += line.product_uom_qty
                rec.total_product_qty_done += line.qty_picked

    @api.depends("location_id", "product_id", "lot_id")
    def _compute_qty_available(self):
        if not self.product_id or self.location_id.usage != "internal":
            self.qty_available = 0.0
            return
        domain_quant = [
            ("product_id", "=", self.product_id.id),
            ("location_id", "=", self.location_id.id),
        ]
        if self.lot_id:
            domain_quant.append(("lot_id", "=", self.lot_id.id))
        # if self.package_id:
        #     domain_quant.append(('package_id', '=', self.package_id.id))
        groups = self.env["stock.quant"].read_group(
            domain_quant, ["quantity"], orderby="id", groupby=["id"]
        )
        self.qty_available = groups[0]["quantity"] if len(groups) > 0 else 0.0
        # Unexpected done quantities must reduce qty_available
        if self.lot_id:
            done_move_lines = self.move_line_ids.filtered(
                lambda m: m.product_id == self.product_id and m.lot_id == self.lot_id
            )
        else:
            done_move_lines = self.move_line_ids.filtered(
                lambda m: m.product_id == self.product_id
            )
        for sml in done_move_lines:
            over_done_qty = float_round(
                sml.quantity - sml.quantity_product_uom,
                precision_rounding=sml.product_uom_id.rounding,
            )
            if over_done_qty > 0.0:
                self.qty_available -= over_done_qty

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

    def _set_candidate_pickings(self, candidate_pickings):
        # Restored from 16.0 — used to refresh the candidate_picking_ids
        # one2many when default picking or onchange picking is set.
        vals = [(5, 0, 0)]
        vals.extend([(0, 0, {"picking_id": p.id}) for p in candidate_pickings])
        self.candidate_picking_ids = vals

    def _search_candidate_picking(self, moves_todo=False):
        # Restored from 16.0 — discovers candidate pickings from the moves
        # currently in scope and either auto-selects the only one or
        # populates the candidate list for the user to pick manually.
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

    def _set_default_picking(self):
        # Restored from 16.0 — picks default picking_id from context and
        # propagates it to candidate_picking_ids.
        picking_id = self.env.context.get("default_picking_id", False)
        if picking_id:
            self._set_candidate_pickings(self.env["stock.picking"].browse(picking_id))

    @api.onchange("picking_id")
    def onchange_picking_id(self):
        self.fill_pending_moves()
        self.determine_todo_action()

    def get_sorted_move_lines(self, move_lines):
        location_field = self.option_group_id.location_field_to_sort
        if not location_field:
            if self.picking_id.picking_type_code in ["incoming", "internal"]:
                location_field = "location_dest_id"
            else:
                location_field = "location_id"
        if self.option_group_id.source_pending_moves == "move_line_ids":
            move_lines = move_lines.sorted(
                lambda sml: (
                    sml[location_field].posx,
                    sml[location_field].posy,
                    sml[location_field].posz,
                    sml[location_field].complete_name,
                )
            )
        else:
            # Stock moves
            move_lines = move_lines.sorted(
                lambda sm: (
                    (sm.move_line_ids[:1] or sm)[location_field].posx,
                    (sm.move_line_ids[:1] or sm)[location_field].posy,
                    (sm.move_line_ids[:1] or sm)[location_field].posz,
                    (sm.move_line_ids[:1] or sm)[location_field].complete_name,
                )
            )
        return move_lines

    def _get_stock_move_lines_todo(self):
        move_lines = self.picking_id.move_line_ids.filtered(
            lambda ml: (not ml.barcode_scan_state or ml.barcode_scan_state == "pending")
            and ml.qty_picked < ml.quantity
        )
        return move_lines

    def fill_pending_moves(self):
        self.fill_todo_records()

    def get_moves_or_move_lines(self):
        if self.option_group_id.source_pending_moves == "move_line_ids":
            return self.picking_id.move_line_ids.filtered(lambda ln: ln.move_id)
        else:
            return self.picking_id.move_ids

    def get_moves(self):
        return self.picking_id.move_ids

    def fill_todo_records(self):
        move_lines = self.get_sorted_move_lines(self.get_moves_or_move_lines())
        self.fill_records([move_lines])

    @api.model
    def _get_fields_filled_special(self):
        return [
            "location_id",
            "location_dest_id",
            "package_id",
            "result_package_id",
            "product_qty",
        ]

    def determine_todo_action(self, forced_todo_line=False):
        self.visible_force_done = self.env.context.get("visible_force_done", False)
        if not self.option_group_id.barcode_guided_mode == "guided":
            return False
        self.todo_line_id = (
            forced_todo_line
            or self.todo_line_ids.filtered(lambda t: t._origin.state == "pending")[:1]
        )
        self.todo_line_id._compute_qty_done()
        move_line = self.todo_line_id
        self.guided_location_id = move_line.location_id
        self.guided_location_dest_id = move_line.location_dest_id
        self.guided_product_id = move_line.product_id
        self.guided_lot_id = move_line.lot_id

        if self.option_group_id.get_option_value("location_id", "filled_default"):
            self.location_id = move_line.location_id
        elif self.option_group_id.get_option_value("location_id", "clean_after_done"):
            self.location_id = False
        if self.option_group_id.get_option_value("location_dest_id", "filled_default"):
            self.location_dest_id = move_line.location_dest_id
        elif self.option_group_id.get_option_value(
            "location_dest_id", "clean_after_done"
        ):
            self.location_dest_id = False
        if self.option_group_id.get_option_value("package_id", "filled_default"):
            self.package_id = move_line.package_id
        if not self.keep_result_package and self.option_group_id.get_option_value(
            "result_package_id", "filled_default"
        ):
            self.result_package_id = move_line.result_package_id
        if self.option_group_id.get_option_value("product_qty", "filled_default"):
            qty_picked = sum(move_line.line_ids.mapped("qty_picked"))
            if move_line.is_stock_move_line_origin:
                pending_qty = move_line.product_qty_reserved - qty_picked
            else:
                pending_qty = move_line.product_uom_qty - qty_picked
            self.product_qty = pending_qty
        else:
            if not self.visible_force_done:
                self.product_qty = 0.0
        # Try to fill data of any field defined in options
        processed_fields = self._get_fields_filled_special()
        for option in self.option_group_id.option_ids:
            if option.field_name in processed_fields:
                continue
            if option.filled_default:
                self[option.field_name] = move_line[option.field_name]
            else:
                if (
                    not self.env.context.get("skip_clean_values", False)
                    and option.clean_after_done
                ):
                    self[option.field_name] = False
        self.update_fields_after_determine_todo(move_line)
        self.action_show_step()

    def update_fields_after_determine_todo(self, move_line):
        # v18: stock.move.line.qty_done was removed; we use qty_picked from
        # stock_move_line_qty_picked extension.
        self.picking_product_qty = move_line.qty_picked

    def refresh_todo_records(self):
        if not self.keep_screen_values or self.todo_line_id.state != "pending":
            if not self.env.context.get("skip_clean_values", False):
                self.action_clean_values()
            keep_vals = {}
        else:
            keep_vals = self._convert_to_write(self._cache)
        self.fill_todo_records()
        if self.forced_todo_key:
            self.todo_line_id = self.pending_move_ids.filtered(
                lambda ln: str(self._group_key(ln)) == self.forced_todo_key
            )[:1]
            self.selected_pending_move_id = self.todo_line_id
            self.determine_todo_action(self.todo_line_id)
        else:
            self.determine_todo_action()
        self.action_show_step()
        if keep_vals:
            self.update_keep_values(keep_vals)

    def action_done(self):
        res = super().action_done()
        if res:
            move_dic = self.with_context(**self.env.context)._process_stock_move_line()
            if move_dic:
                if self.env.context.get("force_create_move"):
                    self.move_line_ids.barcode_scan_state = "done_forced"
                self.refresh_todo_records()
            # Force refresh candidate pickings to show green if not pending moves
            if not self.pending_move_ids:
                pass
                # TODO: Make more visible when picking is done
            return move_dic
        return res

    def update_keep_values(self, keep_vals):
        options = self.option_group_id.option_ids
        fields_to_keep = options.filtered(
            lambda op: self._fields[op.field_name].type != "float"
        ).mapped("field_name")
        self.update({f_name: keep_vals[f_name] for f_name in fields_to_keep})

    def action_manual_entry(self):
        result = super().action_manual_entry()
        if result:
            self.action_done()
        return result

    def _prepare_move_line_values(self, candidate_move, available_qty):
        """When we've got an out picking, the logical workflow is that
        the scanned location is the location we're getting the stock
        from"""
        picking = self.env.context.get("picking", self.picking_id)
        if not picking:
            raise ValidationError(
                _("You can not add extra moves if you have not set a picking")
            )
        # If we move all package units the result package is the same
        if (
            self.package_id
            and not self.result_package_id
            and sum(self.package_id.quant_ids.mapped("quantity")) <= self.product_qty
        ):
            self.result_package_id = self.package_id
        vals = {
            "picking_id": picking.id,
            "move_id": candidate_move.id,
            "qty_picked": available_qty,
            "product_uom_id": candidate_move.product_uom.id or self.product_id.uom_id.id
            if not self.packaging_id
            else self.packaging_id.product_uom_id.id,
            "product_id": self.product_id.id,
            "location_id": self.location_id.id,
            "location_dest_id": self.location_dest_id.id,
            "lot_id": self.lot_id.id,
            "lot_name": self.lot_name,
            "barcode_scan_state": "done_forced",
            "package_id": self.package_id.id,
            "result_package_id": self.result_package_id.id,
        }
        if self.owner_id:
            vals["owner_id"] = self.owner_id.id
        return vals

    def _states_move_allowed(self):
        move_states = ["assigned", "partially_available"]
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

    def _check_guided_restrictions(self):
        # Check restrictions in guided mode
        if self.option_group_id.barcode_guided_mode == "guided":
            if (
                self.option_group_id.get_option_value("product_id", "forced")
                and self.product_id != self.todo_line_id.product_id
            ):
                self._set_messagge_info("more_match", _("Wrong product"))
                return False
        return True

    def _get_candidate_stock_move_lines(self, moves_todo, sml_vals):
        candidate_lines = moves_todo.mapped("move_line_ids").filtered(
            lambda line: (
                # l.picking_id == self.picking_id and
                line.location_id == self.location_id
                and line.location_dest_id == self.location_dest_id
                and line.product_id == self.product_id
            )
        )
        # Try to reuse existing stock move lines updating locations
        if not candidate_lines:
            location_option = self.option_group_id.option_ids.filtered(
                lambda op: op.field_name == "location_id"
            )
            if not location_option.forced:
                candidate_lines = moves_todo.mapped("move_line_ids").filtered(
                    lambda line: (
                        line.location_dest_id == self.location_dest_id
                        and line.product_id == self.product_id
                        and line.location_id == self.picking_location_id
                    )
                )
                if candidate_lines and self.location_id:
                    sml_vals.update({"location_id": self.location_id.id})
        if not candidate_lines:
            location_dest_option = self.option_group_id.option_ids.filtered(
                lambda op: op.field_name == "location_dest_id"
            )
            if not location_dest_option.forced:
                candidate_lines = moves_todo.mapped("move_line_ids").filtered(
                    lambda line: (
                        line.location_id == self.location_id
                        and line.product_id == self.product_id
                        and line.location_dest_id == self.picking_location_dest_id
                    )
                )
                if candidate_lines and self.location_dest_id:
                    sml_vals.update({"location_dest_id": self.location_dest_id.id})
        return candidate_lines

    def _get_candidate_line_domain(self):
        """To be extended for other modules"""
        domain = []
        if self.env.user.has_group("stock.group_tracking_lot"):
            # Check if sml is created with complete content so we fill result package to
            # set the complete package
            if (
                len(self.package_id.quant_ids) == 1
                and float_compare(
                    self.package_id.quant_ids.quantity,
                    self.product_qty,
                    precision_rounding=self.product_id.uom_id.rounding,
                )
                == 0
            ):
                self.result_package_id = self.package_id
            domain.extend(
                [
                    ("package_id", "=", self.package_id.id),
                    ("result_package_id", "=", self.result_package_id.id),
                ]
            )
        return domain

    def _process_stock_move_line(self):  # noqa: C901
        """
        Search assigned or confirmed stock moves from a picking operation type
        or a picking. If there is more than one picking with demand from
        scanned product the interface allow to select what picking to work.
        If only there is one picking the scan data is assigned to it.
        """
        StockMove = self.env["stock.move"]
        domain = self._prepare_stock_moves_domain()
        if self.option_group_id.barcode_guided_mode == "guided":
            moves_todo = self.todo_line_id.stock_move_ids
        elif self.picking_id:
            moves_todo = self.picking_id.move_ids.filtered(
                lambda sm: sm.product_id == self.product_id
            )
        else:
            moves_todo = StockMove.search(domain)
        sml_vals = {}
        candidate_lines = self._get_candidate_stock_move_lines(moves_todo, sml_vals)
        if self.lot_name and not self.lot_id:
            lines = candidate_lines.filtered(
                lambda line: (
                    line.lot_name == self.lot_name
                    and line.barcode_scan_state == "pending"
                )
            )
        else:
            lines = candidate_lines.filtered(
                lambda line: (
                    line.lot_id == self.lot_id and line.barcode_scan_state == "pending"
                )
            )
        # Check if exists lines with lot created if product has tracking serial
        if self.product_id.tracking == "serial":
            serial_lines = self.picking_id.move_line_ids.filtered(
                lambda sml: (
                    (self.lot_id and sml.lot_id == self.lot_id)
                    or (self.lot_name and sml.lot_name == self.lot_name)
                )
                and sml.qty_picked >= 1.0
            )
            if serial_lines:
                self.lot_name = False
                self.lot_id = False
                self._set_messagge_info("more_match", _("S/N Already in picking"))
                return False
        # For incoming pickings the lot is not filled so we try fill it with
        # the lot scanned
        if (
            not lines
            and self.picking_type_code == "incoming"
            and self.product_id.tracking != "none"
        ):
            if (
                self.option_group_id.create_lot
                and self.product_id.tracking == "serial"
                and candidate_lines.filtered(lambda ln: ln.lot_name == self.lot_name)
            ):
                self.lot_name = False
                self.lot_id = False
                self._set_messagge_info("more_match", _("S/N already created"))
                return False
            lines = candidate_lines.filtered(
                lambda line: (not line.lot_id and line.barcode_scan_state == "pending")
            )
            if lines:
                sml_vals.update({"lot_id": self.lot_id.id, "lot_name": self.lot_name})
        candidate_domain = self._get_candidate_line_domain()
        if candidate_domain:
            lines = lines.filtered_domain(candidate_domain)
        # Take into account all smls to get a line to update
        if not lines:
            if self.lot_name:
                lines = candidate_lines.filtered(
                    lambda ln: ln.lot_name == self.lot_name
                )
            else:
                lines = candidate_lines.filtered(lambda ln: ln.lot_id == self.lot_id)
            if candidate_domain:
                lines = lines.filtered_domain(candidate_domain)
        available_qty = self.product_qty
        max_quantity = sum(
            sm.product_uom_qty
            - (sm.qty_picked if sm.qty_picked != sm.product_uom_qty else 0)
            for sm in moves_todo
        )
        if (
            not self.option_group_id.code == "REL"
            and not self.env.context.get("force_create_move", False)
            and not self.env.context.get("manual_picking", False)
            and float_compare(
                available_qty,
                max_quantity,
                precision_rounding=self.product_id.uom_id.rounding,
            )
            > 0
        ):
            self._set_messagge_info(
                "more_match", _("Quantities scanned are higher than necessary.")
            )
            self.visible_force_done = True
            self._set_focus_on_qty_input("product_qty")
            return False
        move_lines_dic = {}
        context = self.env.context
        for line in lines:
            if line.quantity_product_uom and len(lines) > 1:
                assigned_qty = min(
                    max(line.quantity_product_uom - line.qty_picked, 0.0), available_qty
                )
            else:
                assigned_qty = available_qty
            # Not increase qty done if user reads a complete package
            if (
                self.result_package_id
                and self.package_id
                and self.result_package_id == self.package_id
            ):
                qty_done = assigned_qty
            elif context.get("no_increase_qty_done", False) and assigned_qty > 0:
                # Do not increase the quantity, if the quantity is > 0
                qty_done = assigned_qty
            else:
                qty_done = line.qty_picked + assigned_qty
            sml_vals.update(
                {
                    "qty_picked": qty_done,
                    # "quantity": qty_done,
                    "result_package_id": self.result_package_id.id,
                }
            )
            # Add or remove result_pselfackage_id
            package_qty_available = sum(
                self.package_id.quant_ids.filtered(
                    lambda q: q.lot_id == self.lot_id
                ).mapped("quantity")
            )
            if sml_vals["qty_picked"] >= package_qty_available:
                if not self.result_package_id:
                    sml_vals.update({"result_package_id": self.package_id.id})
            elif line.result_package_id == line.package_id:
                sml_vals.update({"result_package_id": False})
            self._update_stock_move_line(line, sml_vals)
            if line.qty_picked >= line.quantity:
                line.barcode_scan_state = "done"
            elif self.env.context.get("done_forced"):
                line.barcode_scan_state = "done_forced"
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
            # When the sml is created we need to link to a stock move but user can read
            # any other product in guided mode so we must ensure that the sm linked to
            # moves to do records have the same product. If not we search any sm linked
            # to the picking.
            moves_to_link = moves_todo.filtered(
                lambda mv: mv.product_id == self.product_id
            )
            # It's possible that there are more than on stock.move with the same product
            # and lot to assign read done, for example, a sale order with two lines with
            # the same product, one of their with a price to zero, in this case we have
            # two equals stock moves and we try to do a repartition between existing
            # stock move lines.
            stock_move_lines = self.env["stock.move.line"].browse()
            more_than_one_move = len(moves_to_link) > 1
            for move_to_link in moves_to_link:
                if more_than_one_move:
                    reserved_qty = sum(
                        move_to_link.move_line_ids.mapped("quantity_product_uom")
                    )
                    qty_picked = sum(move_to_link.move_line_ids.mapped("qty_picked"))
                    assigned_qty = min(
                        max(reserved_qty - qty_picked, 0.0), available_qty
                    )
                else:
                    assigned_qty = available_qty
                if (
                    float_compare(
                        assigned_qty,
                        0,
                        precision_rounding=self.product_id.uom_id.rounding,
                    )
                    > 0
                ):
                    stock_move_lines += self.create_new_stock_move_line(
                        move_to_link, assigned_qty
                    )
                    available_qty -= assigned_qty
                if (
                    float_compare(
                        available_qty,
                        0,
                        precision_rounding=self.product_id.uom_id.rounding,
                    )
                    < 0
                ):
                    break
            if (
                float_compare(
                    available_qty, 0, precision_rounding=self.product_id.uom_id.rounding
                )
                > 0
            ):
                # After distributing the amount read, I still have an amount to
                # distribute, and I assign it to the first movement.
                stock_move_lines += self.create_new_stock_move_line(
                    moves_to_link[:1], available_qty
                )
            move_to_link_in_todo_line = True
            if not moves_to_link:
                move_to_link_in_todo_line = False
            for sml in stock_move_lines:
                if not sml.move_id:
                    self.create_new_stock_move(sml)
                move_lines_dic[sml.id] = sml.qty_picked
            # Ensure that the state of stock_move linked to the sml read is assigned
            stock_move_lines.move_id.filtered(
                lambda sm: sm.state == "draft"
            ).state = "assigned"
            # When create new stock move lines and we are in guided mode we need
            # link this new lines to the todo line details
            # If user scan a product distinct of the todo line we need link to other
            # alternative move
            if self.option_group_id.source_pending_moves != "move_line_ids":
                if move_to_link_in_todo_line and self.todo_line_id:
                    todo_line = self.todo_line_id
                else:
                    todo_line = self.todo_line_ids.filtered(
                        lambda ln: ln.product_id == self.product_id
                    )
                todo_line.line_ids = [(4, sml.id) for sml in stock_move_lines]
        self.update_fields_after_process_stock(moves_todo)
        return move_lines_dic

    def _update_stock_move_line(self, line, sml_vals):
        """Update stock move line with values. Helper method to be inherited"""
        line.write(sml_vals)

    def create_new_stock_move_line(self, moves_todo, available_qty):
        """Create a new stock move line when a sml is not available
        for the wizard values.
        """
        return self.env["stock.move.line"].create(
            self._prepare_move_line_values(moves_todo[:1], available_qty)
        )

    def create_new_stock_move(self, sml):
        vals = {
            "name": _("New Move:") + sml.product_id.display_name,
            "product_uom": sml.product_uom_id.id,
            "product_uom_qty": sml.qty_picked,
            "state": "assigned",
            "additional": True,
            "product_id": sml.product_id.id,
            "location_id": sml.location_id.id,
            "location_dest_id": sml.location_dest_id.id,
            "picking_id": sml.picking_id.id,
        }
        new_move = self.env["stock.move"].create(vals)
        sml.move_id = new_move

    def update_fields_after_process_stock(self, moves):
        self.picking_product_qty = sum(moves.mapped("quantity"))

    def check_done_conditions(self):
        res = super().check_done_conditions()
        if (
            not self.option_group_id.allow_not_demanded_product
            and self.product_id not in self.todo_line_ids.product_id
        ):
            self._set_messagge_info("not_found", _("Product not demanded"))
            return False
        if (
            self.picking_type_code != "incoming"
            and float_compare(
                self.product_qty,
                self.qty_available,
                precision_rounding=self.product_id.uom_id.rounding or 1,
            )
            > 0
            and not self.env.context.get("force_create_move", False)
            and not self.option_group_id.allow_negative_quant
        ):
            self._set_messagge_info(
                "more_match", _("Quantities not available in location")
            )
            if self.option_group_id.allow_negative_quant:
                self.visible_force_done = True
            # Set focus on product_qty input box
            self._set_focus_on_qty_input("product_qty")
            return False
        if self.picking_mode == "picking_batch":
            return res
        if not self.picking_id:
            self._set_messagge_info("info", _("No picking selected"))
            return False
        return res

    def get_lot_by_removal_strategy(self):
        quants = first(
            self.env["stock.quant"]._gather(self.product_id, self.location_id)
        )
        # TODO: Perhaps update location_id from quant??
        self.lot_id = quants.lot_id

    def action_product_scaned_post(self, product):
        res = super().action_product_scaned_post(product)
        if self.auto_lot and self.picking_type_code != "incoming":
            self.get_lot_by_removal_strategy()
        return res

    def action_assign_serial(self):
        move = self.env["stock.move"].search(self._prepare_stock_moves_domain())
        if len(move) > 1:
            smls = move.move_line_ids.filtered(
                lambda ln: ln.barcode_scan_state == "pending"
            )
            move = smls[:1].move_id
        if move:
            return move.action_assign_serial()
        raise ValidationError(_("No pending lines for this product"))

    def action_put_in_pack(self):
        for picking in self.mapped("picking_id"):
            picking.action_put_in_pack()

    def action_clean_values(self):
        res = super().action_clean_values()
        self.selected_pending_move_id = False
        self.visible_force_done = False
        # Hide Form Edit
        self.manual_entry = False
        self.send_bus_done(
            "stock_barcodes_scan",
            {
                "type": "stock_barcodes_edit_manual",
                "payload": {
                    "manual_entry": False,
                },
            },
        )
        return res

    def _option_required_hook(self, option_required):
        if (
            option_required.field_name == "location_dest_id"
            and self.option_group_id.use_location_dest_putaway
        ):
            self.location_dest_id = self.picking_id.location_dest_id.with_context(
                avoid_location_with_reserve=True
            )._get_putaway_strategy(
                self.product_id,
                quantity=self.product_qty,
                package=self.result_package_id,
                packaging=self.packaging_id,
            )
            return bool(self.location_dest_id)
        return super()._option_required_hook(option_required)

    def _group_key(self, line):
        group_key_for_todo_records = self.option_group_id.group_key_for_todo_records
        if group_key_for_todo_records:
            return safe_eval(group_key_for_todo_records, globals_dict={"object": line})
        if self.option_group_id.source_pending_moves == "move_line_ids":
            return (
                line.location_id.id,
                line.product_id.id,
                line.lot_id.id,
                line.package_id.id,
            )
        else:
            return (line.location_id.id, line.product_id.id)

    def _get_location_domain_for_quant_search(self):
        if self.picking_id:
            return [("location_id", "child_of", self.picking_id.location_id.ids)]
        return super()._get_location_domain_for_quant_search()

    def _get_all_products_quantities_in_package(self, package):
        res = {}
        # TODO: Check if domain is applied and we must recover _get_contained_quants
        for quant in package.quant_ids:
            if quant.product_id not in res:
                res[quant.product_id] = 0
            res[quant.product_id] += quant.quantity
        return res

    def _prepare_fill_record_values(self, line, position):
        vals = {
            "wiz_barcode_id": self.id,
            "product_id": line.product_id.id,
            "name": "To do action",
            "position_index": position,
            "picking_code": line.picking_code,
        }
        if line._name == "stock.move.line":
            package_product_dic = self._get_all_products_quantities_in_package(
                line.package_id
            )
            vals.update(
                {
                    "location_id": line.location_id.id,
                    "location_dest_id": line.location_dest_id.id,
                    "lot_id": line.lot_id.id,
                    "package_id": line.package_id.id,
                    "result_package_id": line.result_package_id.id,
                    "uom_id": line.product_uom_id.id,
                    # Initialize aggregation counters so _update_fill_record_values
                    # can += on subsequent calls (v18 field renames: reserved_uom_qty
                    # -> quantity_product_uom; reserved_qty -> quantity).
                    "product_uom_qty": line.quantity_product_uom,
                    "product_qty_reserved": line.quantity,
                    "line_ids": [(6, 0, line.ids)],
                    "stock_move_ids": [(6, 0, line.move_id.ids)],
                    "package_product_qty": package_product_dic
                    and package_product_dic[line.product_id]
                    or 0.0,
                    "is_stock_move_line_origin": True,
                }
            )
        else:
            vals.update(
                {
                    "location_id": (line.move_line_ids[:1] or line).location_id.id,
                    "location_dest_id": (
                        line.move_line_ids[:1] or line
                    ).location_dest_id.id,
                    "uom_id": line.product_uom.id,
                    "product_uom_qty": line.product_uom_qty,
                    "product_qty_reserved": (
                        sum(line.move_line_ids.mapped("quantity"))
                        if line.move_line_ids
                        else line.product_uom_qty
                    ),
                    "line_ids": [(6, 0, line.move_line_ids.ids)],
                    "stock_move_ids": [(6, 0, line.ids)],
                    "is_stock_move_line_origin": False,
                }
            )
        return vals

    def _update_fill_record_values(self, line, vals):
        # Restored aggregation logic from 16.0 with v18 field renames:
        # reserved_uom_qty -> quantity_product_uom; reserved_qty -> quantity
        # (sum of currently reserved qty on move lines).
        if vals["is_stock_move_line_origin"]:
            vals["product_uom_qty"] += line.quantity_product_uom
            vals["product_qty_reserved"] += line.quantity
            vals["line_ids"][0][2].append(line.id)
            vals["stock_move_ids"][0][2].append(line.move_id.id)
            if line.lot_id and line.lot_id.id != vals.get("lot_id", False):
                vals["lot_id"] = False
        else:
            vals["product_uom_qty"] += line.product_uom_qty
            vals["product_qty_reserved"] += (
                line.move_line_ids
                and sum(line.move_line_ids.mapped("quantity"))
                or line.product_uom_qty
            )
            vals["line_ids"][0][2].extend(line.move_line_ids.ids)
            vals["stock_move_ids"][0][2].extend(line.ids)
        return vals

    @api.model
    def fill_records(self, lines_list):
        """
        :param lines_list: browse list
        :return:
        """
        self.forced_todo_key = str(
            self._group_key(self.todo_line_id or self.selected_pending_move_id)
        )
        self.todo_line_ids.unlink()
        self.todo_line_id = False
        # self.position_index = 0
        todo_vals = OrderedDict()
        position = 0
        move_qty_dic = defaultdict(float)
        is_stock_move_line_origin = lines_list[0]._name == "stock.move.line"
        for lines in lines_list:
            for line in lines:
                key = self._group_key(line)
                if key not in todo_vals:
                    todo_vals[key] = self._prepare_fill_record_values(line, position)
                    position += 1
                else:
                    todo_vals[key] = self._update_fill_record_values(
                        line, todo_vals[key]
                    )
                # Max between the reserved and picked..
                move = line.move_id if is_stock_move_line_origin else line
                move_qty_dic[move] += max(line.quantity, line.qty_picked)
        for move in self.get_moves():
            qty = move_qty_dic[move]
            if (
                move.barcode_backorder_action == "pending"
                and move.product_uom_qty > qty
            ):
                vals = self._prepare_fill_record_values(move, position)
                vals.update(
                    {
                        "product_uom_qty": move.product_uom_qty - qty,
                        "product_qty_reserved": 0.0,
                        "line_ids": False,
                        "is_extra_line": True,
                    }
                )
                todo_vals[
                    (
                        move,
                        "M",
                    )
                ] = vals
                position += 1
        self.todo_line_ids = self.env["wiz.stock.barcodes.read.todo"].create(
            list(todo_vals.values())
        )

    def action_open_picking(self):
        return self.picking_id.with_context(
            control_panel_hidden=False
        ).get_formview_action()

    def _candidate_picking_selected(self):
        # Restored from 16.0 — when there's exactly one candidate picking it
        # is the implicit selection, otherwise an empty recordset.
        if len(self.candidate_picking_ids) == 1:
            return self.candidate_picking_ids.picking_id
        else:
            return self.env["stock.picking"].browse()

    def action_unlock_picking(self):
        # Restored from 16.0 — delegates the unlock to each candidate picking
        # row so the wizard goes back to the candidate-listing screen.
        for candidate_picking in self.candidate_picking_ids:
            candidate_picking.with_context(
                wiz_barcode_id=self.id
            ).action_unlock_picking()

    def action_lock_picking(self):
        # Restored from 16.0 — locks the current picking via each candidate
        # picking row (symmetric of action_unlock_picking).
        for candidate_picking in self.candidate_picking_ids:
            candidate_picking.with_context(
                wiz_barcode_id=self.id, picking_id=self.picking_id.id
            ).action_lock_picking()

    def get_action_after_validate(self):
        if not self.picking_id:
            return False
        action = self.picking_id.picking_type_id.get_action_picking_tree_ready()
        return action

    def _get_picking_to_validate(self):
        """Inject context action to redirect it after validate picking in barcodes
        environment.
        The stock_barcodes_validate_picking key allows to know when a picking has been
        validated from stock barcodes interface.
        """
        return self.picking_id.with_context(
            stock_barcodes_validate_picking=True,
        )

    def action_validate_picking(self):
        # Restored from 16.0 — delegate the actual validation to each
        # wiz.candidate.picking row (which knows how to deal with the
        # immediate-transfer wizard) and only build the post-validate
        # action when the delegation reports success.
        valid, result = self.candidate_picking_ids.with_context(
            wiz_barcode_id=self.id,
            picking_id=self.picking_id.id,
            skip_sms=True,
            skip_immediate=True,
        ).action_validate_picking()
        if not valid:
            return result
        action = self.env["ir.actions.actions"]._for_xml_id(
            "stock_barcodes.stock_barcodes_action_picking_tree_ready"
        )
        if self.picking_id and self.picking_id.picking_type_id:
            context = self.env.context.copy()
            context.update(safe_eval(action["context"]))
            context.update(
                {"search_default_picking_type_id": self.picking_id.picking_type_id.id}
            )
            action["context"] = context
        return action

    def _get_moves_from_product_domain(self):
        return [
            ("picking_code", "=", self.picking_type_code),
            ("state", "in", ["assigned", "partially_available"]),
            ("product_id", "=", self.product_id.id),
        ]

    def get_picking_from_product(self):
        moves = self.env["stock.move"].search(self._get_moves_from_product_domain())
        pickings = moves.picking_id
        return pickings

    def action_picking_from_product(self):
        if (
            not self.picking_id
            and self.option_group_id.search_picking_from_product
            and self.product_id
        ):
            pickings = self.get_picking_from_product()
            if not pickings:
                return False
            if self.option_group_id.search_picking_from_product == "first":
                self.picking_id = pickings[:1]
            elif self.option_group_id.search_picking_from_product == "last":
                self.picking_id = pickings[-1:]
            self.picking_mode = "picking"
            self.res_model_id = self.env.ref("stock.model_stock_picking").id
            self.res_id = self.picking_id.id
            return self.picking_id.action_barcode_scan(wiz=self)
        else:
            return False

    def process_barcode(self, barcode):
        res = super().process_barcode(barcode)
        if not res:
            action = self.action_picking_from_product()
            if action:
                return action
        return res

    def action_confirm(self):
        action = self.action_picking_from_product()
        res = super().action_confirm()
        if res and action:
            return action
        return res
