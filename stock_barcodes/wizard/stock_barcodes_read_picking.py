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

    @property
    @api.depends("picking_mode")
    def _field_candidate_ids(self):
        return "candidate_%s_ids" % self.picking_mode

    picking_id = fields.Many2one(
        comodel_name="stock.picking", string="Picking", readonly=True
    )
    picking_state = fields.Selection(related="picking_id.state")
    picking_ids = fields.Many2many(
        comodel_name="stock.picking", string="Pickings", readonly=True
    )
    candidate_picking_ids = fields.One2many(
        comodel_name="wiz.candidate.picking",
        inverse_name="wiz_barcode_id",
        string="Candidate pickings",
        readonly=True,
    )
    # TODO: Remove this field
    picking_product_qty = fields.Float(
        string="Picking quantities", digits="Product Unit of Measure", readonly=True
    )
    picking_type_code = fields.Selection(
        [("incoming", "Vendors"), ("outgoing", "Customers"), ("internal", "Internal")],
        "Type of Operation",
    )
    # TODO: Check if move_line_ids is used
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
        related="option_group_id.show_detailed_operations"
    )
    keep_screen_values = fields.Boolean(related="option_group_id.keep_screen_values")
    # Extended from stock_barcodes_read base model
    total_product_uom_qty = fields.Float(compute="_compute_total_product")
    total_product_qty_done = fields.Float(compute="_compute_total_product")

    @api.depends("todo_line_id")
    def _compute_todo_line_display_ids(self):
        """Technical field to display only the first record in kanban view"""
        self.todo_line_display_ids = self.todo_line_id

    @api.depends("todo_line_ids")
    def _compute_pending_move_ids(self):
        if self.option_group_id.show_pending_moves:
            self.pending_move_ids = self.todo_line_ids.filtered(
                lambda t: t.state == "pending"
            )
        else:
            self.pending_move_ids = False

    @api.depends("todo_line_ids")
    def _compute_move_line_ids(self):
        self.move_line_ids = self.picking_id.move_line_ids.filtered("qty_done").sorted(
            key=lambda sml: (sml.write_date, sml.create_date), reverse=True
        )

    @api.depends("picking_id.move_line_ids.qty_done")
    def _compute_total_product(self):
        self.total_product_uom_qty = 0.0
        self.total_product_qty_done = 0.0
        for rec in self:
            product_moves = rec.picking_id.move_lines.filtered(
                lambda ln: ln.product_id.ids == self.product_id.ids
                and ln.state != "cancel"
            )
            for line in product_moves:
                rec.total_product_uom_qty += line.product_uom_qty
                rec.total_product_qty_done += line.quantity_done

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
        self.determine_todo_action()
        self.fill_pending_moves()

    def get_sorted_move_lines(self, move_lines):
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
                    sml[location_field].name,
                )
            )
        else:
            # Stock moves
            move_lines = move_lines.sorted(
                lambda sm: (
                    (sm.move_line_ids[:1] or sm)[location_field].posx,
                    (sm.move_line_ids[:1] or sm)[location_field].posy,
                    (sm.move_line_ids[:1] or sm)[location_field].posz,
                    (sm.move_line_ids[:1] or sm)[location_field].name,
                )
            )
        return move_lines

    def _get_stock_move_lines_todo(self):
        move_lines = self.picking_id.move_line_ids.filtered(
            lambda ml: (not ml.barcode_scan_state or ml.barcode_scan_state == "pending")
            and ml.qty_done < ml.product_qty
        )
        return move_lines

    def fill_pending_moves(self):
        if (
            self.option_group_id.barcode_guided_mode != "guided"
            and self.option_group_id.show_pending_moves
            and not self.todo_line_ids
        ):
            self.fill_todo_records()

    def get_moves_or_move_lines(self):
        if self.option_group_id.source_pending_moves == "move_line_ids":
            return self.picking_id.move_line_ids.filtered(lambda ln: ln.move_id)
        else:
            return self.picking_id.move_lines

    def fill_todo_records(self):
        move_lines = self.get_sorted_move_lines(self.get_moves_or_move_lines())
        self.env["wiz.stock.barcodes.read.todo"].fill_records(self, [move_lines])

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
        if not self.todo_line_ids:
            self.fill_todo_records()
        # When scanning all information in one step (e.g. using GS-1), the
        # status and qty processed might have not been update, we ensure it
        # invalidating the cache.
        self.todo_line_ids.invalidate_cache()
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
        elif self.picking_type_code != "incoming":
            self.location_id = False
        if self.option_group_id.get_option_value("location_dest_id", "filled_default"):
            self.location_dest_id = move_line.location_dest_id
        elif self.picking_type_code != "outgoing":
            self.location_dest_id = False
        if self.option_group_id.get_option_value("package_id", "filled_default"):
            self.package_id = move_line.package_id
        if not self.keep_result_package and self.option_group_id.get_option_value(
            "result_package_id", "filled_default"
        ):
            self.result_package_id = move_line.result_package_id
        if self.option_group_id.get_option_value("product_qty", "filled_default"):
            self.product_qty = move_line.product_uom_qty - move_line.qty_done
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
                if not self.env.context.get("skip_clean_values", False):
                    self[option.field_name] = False
        self.update_fields_after_determine_todo(move_line)
        self.action_show_step()

    def update_fields_after_determine_todo(self, move_line):
        self.picking_product_qty = move_line.qty_done

    def action_done(self):
        # Skip read log creation to be able to pass log_detail when available.
        res = super(
            WizStockBarcodesReadPicking,
            self.with_context(_stock_barcodes_skip_read_log=True),
        ).action_done()
        if res:
            move_dic = self._process_stock_move_line()
            if move_dic:
                self[self._field_candidate_ids].scan_count += 1
                if self.env.context.get("force_create_move"):
                    self.move_line_ids.barcode_scan_state = "done_forced"
                if not self.keep_screen_values or self.todo_line_id.state != "pending":
                    if not self.env.context.get("skip_clean_values", False):
                        self.action_clean_values()
                    self.determine_todo_action()
                else:
                    self.action_show_step()
            # Now we can add read log with details.
            _logger.info("Add scanned log barcode:{}".format(self.barcode))
            self._add_read_log(log_detail=move_dic)
            return move_dic
        # Add read log normally.
        _logger.info("Add scanned log barcode:{}".format(self.barcode))
        self._add_read_log()
        return res

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
                _("You can not add extra moves if you have " "not set a picking")
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
            "qty_done": available_qty,
            "product_uom_id": candidate_move.product_uom.id or self.product_id.uom_id.id
            if not self.packaging_id
            else self.packaging_id.product_uom_id.id,
            "product_id": self.product_id.id,
            "location_id": self.location_id.id,
            "location_dest_id": self.location_dest_id.id,
            "lot_id": self.lot_id.id,
            "lot_name": self.lot_id.name,
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

    def _set_candidate_pickings(self, candidate_pickings):
        vals = [(5, 0, 0)]
        vals.extend([(0, 0, {"picking_id": p.id}) for p in candidate_pickings])
        self.candidate_picking_ids = vals

    def _search_candidate_picking(self, moves_todo=False):
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
            lambda l: (
                # l.picking_id == self.picking_id and
                l.location_id == self.location_id
                and l.location_dest_id == self.location_dest_id
                and l.product_id == self.product_id
            )
        )
        if not candidate_lines:
            location_option = self.option_group_id.option_ids.filtered(
                lambda op: op.field_name == "location_id"
            )
            if not location_option.forced:
                candidate_lines = moves_todo.mapped("move_line_ids").filtered(
                    lambda l: (
                        l.location_dest_id == self.location_dest_id
                        and l.product_id == self.product_id
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
                    lambda l: (
                        l.location_id == self.location_id
                        and l.product_id == self.product_id
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
        else:
            moves_todo = StockMove.search(domain)
        if not getattr(
            self,
            "_search_candidate_%s" % self.picking_mode,
        )(moves_todo):
            return False
        sml_vals = {}
        candidate_lines = self._get_candidate_stock_move_lines(moves_todo, sml_vals)
        lines = candidate_lines.filtered(
            lambda l: (l.lot_id == self.lot_id and l.barcode_scan_state == "pending")
        )
        # Check if exists lines with lot created if product has tracking serial
        if self.product_id.tracking == "serial":
            serial_lines = self.picking_id.move_line_ids.filtered(
                lambda sml: (
                    sml.lot_id == self.lot_id or sml.lot_name == self.lot_id.name
                )
                and sml.qty_done >= 1.0
            )
            if serial_lines:
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
                and candidate_lines.filtered(lambda ln: ln.lot_name == self.lot_id.name)
            ):
                self.lot_id = False
                self._set_messagge_info("more_match", _("S/N already created"))
                return False
            lines = candidate_lines.filtered(
                lambda l: (not l.lot_id and l.barcode_scan_state == "pending")
            )
            if lines:
                sml_vals.update(
                    {"lot_id": self.lot_id.id, "lot_name": self.lot_id.name}
                )
        candidate_domain = self._get_candidate_line_domain()
        if candidate_domain:
            lines = lines.filtered_domain(candidate_domain)
        # Take into account all smls to get a line to update
        if not lines:
            lines = candidate_lines.filtered(lambda ln: (ln.lot_id == self.lot_id))
            if candidate_domain:
                lines = lines.filtered_domain(candidate_domain)
        available_qty = self.product_qty
        max_quantity = sum(sm.product_uom_qty - sm.quantity_done for sm in moves_todo)
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
                "more_match", _("Quantities scanned are higher than necessary")
            )
            self.visible_force_done = True
            self._set_focus_on_qty_input("product_qty")
            return False
        move_lines_dic = {}
        for line in lines:
            if line.product_uom_qty and len(lines) > 1:
                assigned_qty = min(
                    max(line.product_uom_qty - line.qty_done, 0.0), available_qty
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
            else:
                qty_done = line.qty_done + assigned_qty
            sml_vals.update(
                {
                    "qty_done": qty_done,
                    "result_package_id": self.result_package_id.id,
                }
            )
            # Add or remove result_package_id
            package_qty_available = sum(
                self.package_id.quant_ids.filtered(
                    lambda q: q.lot_id == self.lot_id
                ).mapped("quantity")
            )
            if sml_vals["qty_done"] >= package_qty_available:
                if not self.result_package_id:
                    sml_vals.update({"result_package_id": self.package_id.id})
            elif line.result_package_id == line.package_id:
                sml_vals.update({"result_package_id": False})
            self._update_stock_move_line(line, sml_vals)
            if line.qty_done >= line.product_uom_qty:
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
            # moves todo records have the same product. If not we search any sm linked
            # to the picking.
            moves_to_link = moves_todo.filtered(
                lambda mv: mv.product_id == self.product_id
            )
            move_to_link_in_todo_line = True
            if not moves_to_link:
                move_to_link_in_todo_line = False
                moves_to_link = self.picking_id.move_lines.filtered(
                    lambda mv: mv.product_id == self.product_id
                )
            stock_move_lines = self.create_new_stock_move_line(
                moves_to_link, available_qty
            )
            for sml in stock_move_lines:
                if not sml.move_id:
                    self.create_new_stock_move(sml)
                move_lines_dic[sml.id] = sml.qty_done
            # When create new stock move lines and we are in guided mode we need
            # link this new lines to the todo line details
            if self.option_group_id.barcode_guided_mode == "guided":
                # If user scan a product distinct of the todo line we need link to other
                # alternative move
                if move_to_link_in_todo_line:
                    todo_line = self.todo_line_id
                else:
                    todo_line = self.todo_line_ids.filtered(
                        lambda ln: ln.product_id == self.product_id
                    )
                todo_line.line_ids = [(4, sml.id) for sml in stock_move_lines]
            elif self.option_group_id.show_pending_moves:
                # TODO: Check performance with a lot records
                self.fill_todo_records()
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
            "product_uom_qty": sml.qty_done,
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
        self.picking_product_qty = sum(moves.mapped("quantity_done"))

    def _candidate_picking_selected(self):
        if len(self.candidate_picking_ids) == 1:
            return self.candidate_picking_ids.picking_id
        else:
            return self.env["stock.picking"].browse()

    def check_done_conditions(self):
        res = super().check_done_conditions()
        if (
            self.picking_type_code != "incoming"
            and float_compare(
                self.product_qty,
                self.qty_available,
                precision_rounding=self.product_id.uom_id.rounding,
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
            if not self._search_candidate_picking():
                self._set_messagge_info(
                    "info", _("Click on picking pushpin to lock it")
                )
                return False
        if self.picking_id and self.picking_id != self._candidate_picking_selected():
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
                sml = log_scan_line.move_line_id
                if sml.state not in ["draft", "assigned", "confirmed"]:
                    raise ValidationError(
                        _(
                            "You cannot remove an entry linked to a operation "
                            "in state new, assigned or confirmed"
                        )
                    )
                qty = sml.qty_done - log_scan_line.product_qty
                log_scan_line.move_line_id.qty_done = max(qty, 0.0)
                if sml.state == "draft" and sml.move_id.quantity_done == 0.0:
                    # This move has been created by the last scan, remove it.
                    sml.move_id.unlink()
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
        self.picking_id.action_put_in_pack()

    def action_clean_values(self):
        res = super().action_clean_values()
        self.selected_pending_move_id = False
        self.visible_force_done = False
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
    is_pending = fields.Boolean(compute="_compute_is_pending")
    note = fields.Html(related="picking_id.note")

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

    @api.depends("scan_count")
    def _compute_is_pending(self):
        for rec in self:
            rec.is_pending = bool(rec.wiz_barcode_id.pending_move_ids)

    def _get_wizard_barcode_read(self):
        return self.env["wiz.stock.barcodes.read.picking"].browse(
            self.env.context["wiz_barcode_id"]
        )

    def action_lock_picking(self):
        wiz = self._get_wizard_barcode_read()
        picking_id = self.env.context["picking_id"]
        wiz.picking_id = picking_id
        wiz._set_candidate_pickings(wiz.picking_id)
        return wiz.action_confirm()

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

    def _get_picking_to_validate(self):
        """Inject context show_picking_type_action_tree to redirect to picking list
        after validate picking in barcodes environment.
        The stock_barcodes_validate_picking key allows to know when a picking has been
        validated from stock barcodes interface.
        """
        return (
            self.env["stock.picking"]
            .browse(self.env.context.get("picking_id", False))
            .with_context(
                show_picking_type_action_tree=True, stock_barcodes_validate_picking=True
            )
        )

    def action_validate_picking(self):
        picking = self._get_picking_to_validate()
        return picking.button_validate()

    def action_open_picking(self):
        picking = self.env["stock.picking"].browse(
            self.env.context.get("picking_id", False)
        )
        return picking.with_context(control_panel_hidden=False).get_formview_action()

    def action_put_in_pack(self):
        self.picking_id.action_put_in_pack()
