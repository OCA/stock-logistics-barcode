# Copyright 2019 Sergio Teruel <sergio.teruel@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
from odoo.tools.float_utils import float_compare


class WizStockBarcodesReadTodo(models.TransientModel):
    _name = "wiz.stock.barcodes.read.todo"
    _description = "Wizard to read barcode todo"

    # To prevent remove the record wizard until 2 days old
    _transient_max_hours = 48

    name = fields.Char()
    wiz_barcode_id = fields.Many2one(comodel_name="wiz.stock.barcodes.read.picking")
    picking_state = fields.Selection(related="wiz_barcode_id.picking_state")
    partner_id = fields.Many2one(
        comodel_name="res.partner",
        readonly=True,
        string="Partner",
    )
    state = fields.Selection(
        [("pending", "Pending"), ("done", "Done"), ("done_forced", "Done forced")],
        string="Scan State",
        default="pending",
        compute="_compute_state",
        readonly=False,
    )

    product_qty_reserved = fields.Float(
        "Reserved",
        digits="Product Unit of Measure",
        readonly=True,
    )
    product_uom_qty = fields.Float(
        "Demand",
        digits="Product Unit of Measure",
        readonly=True,
    )
    qty_done = fields.Float(
        "Done",
        digits="Product Unit of Measure",
        compute="_compute_qty_done",
    )
    qty_done_rest = fields.Float(compute="_compute_qty_done_rest", store=True)
    location_id = fields.Many2one(comodel_name="stock.location")
    location_name = fields.Char(related="location_id.name")
    location_dest_id = fields.Many2one(comodel_name="stock.location")
    location_dest_name = fields.Char(
        string="Destinatino Name", related="location_dest_id.name"
    )
    product_id = fields.Many2one(comodel_name="product.product")
    lot_id = fields.Many2one(comodel_name="stock.lot")
    uom_id = fields.Many2one(comodel_name="uom.uom")
    package_id = fields.Many2one(comodel_name="stock.quant.package")
    result_package_id = fields.Many2one(comodel_name="stock.quant.package")
    package_product_qty = fields.Float()

    res_model_id = fields.Many2one(comodel_name="ir.model")
    res_ids = fields.Char()
    line_ids = fields.Many2many(comodel_name="stock.move.line")
    stock_move_ids = fields.Many2many(comodel_name="stock.move")
    position_index = fields.Integer()
    picking_code = fields.Char("Type of Operation")
    is_extra_line = fields.Boolean()
    # Used in kanban view
    is_stock_move_line_origin = fields.Boolean()

    @api.depends("qty_done", "product_uom_qty")
    def _compute_qty_done_rest(self):
        for rec in self:
            rec.qty_done_rest = rec.product_uom_qty - rec.qty_done

    def action_todo_next(self):
        self.state = "done_forced"
        self.line_ids.barcode_scan_state = "done_forced"
        for sml in self.line_ids:
            if (
                float_compare(
                    sml.reserved_uom_qty,
                    sml.qty_done,
                    precision_rounding=sml.product_uom_id.rounding,
                )
                == 0
            ):
                continue
            if sml.move_id.state == "confirmed" and sml.qty_done:
                sml.move_id.state = "partially_available"
            if sml.move_id.state in ["partially_available", "assigned"]:
                sml.reserved_uom_qty = sml.qty_done
        if self.is_extra_line or not self.is_stock_move_line_origin:
            barcode_backorder_action = self.env.context.get(
                "barcode_backorder_action", "create_backorder"
            )
            self.stock_move_ids.barcode_backorder_action = barcode_backorder_action
            if barcode_backorder_action == "pending":
                self.stock_move_ids.move_line_ids.unlink()
                self.stock_move_ids._action_assign()
        wiz_barcode = self.wiz_barcode_id
        self.wiz_barcode_id.fill_todo_records()
        self.wiz_barcode_id = wiz_barcode
        self.wiz_barcode_id.determine_todo_action()

    def action_reset_lines(self):
        self.state = "pending"
        self.line_ids.barcode_scan_state = "pending"
        self.line_ids.qty_done = 0.0
        self.wiz_barcode_id.action_clean_values()
        self.wiz_barcode_id.fill_todo_records()
        self.wiz_barcode_id.determine_todo_action()

    def action_back_line(self):
        if self.position_index > 0:
            record = self.wiz_barcode_id.todo_line_ids[self.position_index - 1]
            self.wiz_barcode_id.determine_todo_action(forced_todo_line=record)

    def action_next_line(self):
        if self.position_index < len(self.wiz_barcode_id.todo_line_ids) - 1:
            record = self.wiz_barcode_id.todo_line_ids[self.position_index + 1]
            self.wiz_barcode_id.determine_todo_action(forced_todo_line=record)

    @api.depends("line_ids.qty_done")
    def _compute_qty_done(self):
        for rec in self:
            rec.qty_done = sum(ln.qty_done for ln in rec.line_ids)

    @api.depends(
        "line_ids",
        "line_ids.qty_done",
        "line_ids.reserved_uom_qty",
        "line_ids.barcode_scan_state",
        "qty_done",
        "product_uom_qty",
    )
    def _compute_state(self):
        for rec in self:
            if float_compare(
                rec.qty_done,
                rec.product_uom_qty,
                precision_rounding=rec.uom_id.rounding,
            ) > -1 or (
                rec.wiz_barcode_id.option_group_id.source_pending_moves
                == "move_line_ids"
                and rec.line_ids
                and (
                    sum(rec.stock_move_ids.mapped("quantity_done"))
                    >= sum(rec.stock_move_ids.mapped("product_uom_qty"))
                    or not any(
                        ln.barcode_scan_state == "pending" for ln in rec.line_ids
                    )
                )
            ):
                rec.state = "done"
            else:
                rec.state = "pending"

    @api.model
    def fields_to_fill_from_pending_line(self):
        res = [
            "location_id",
            "location_dest_id",
            "product_id",
            "lot_id",
            "package_id",
        ]
        if not self.wiz_barcode_id.keep_result_package:
            res.append("result_package_id")
        return res

    def fill_from_pending_line(self):
        self.wiz_barcode_id.selected_pending_move_id = self
        self.wiz_barcode_id.determine_todo_action(forced_todo_line=self)
        for field in self.fields_to_fill_from_pending_line():
            self.wiz_barcode_id[field] = self[field]
        # Force fill product_qty if filled_default is set
        if self.wiz_barcode_id.option_group_id.get_option_value(
            "product_qty", "filled_default"
        ):
            self.wiz_barcode_id.product_qty = self.product_uom_qty - sum(
                self.line_ids.mapped("qty_done")
            )
        self.wiz_barcode_id.product_uom_id = self.uom_id
        self.wiz_barcode_id.action_show_step()
        self.wiz_barcode_id._set_focus_on_qty_input()

    def operation_quantities(self):
        self.wiz_barcode_id.manual_entry = True
        self.wiz_barcode_id.product_qty = self.product_qty_reserved
        self.wiz_barcode_id.product_id = self.product_id.id
        if self.wiz_barcode_id.picking_id.picking_type_id.code != "incoming":
            self.wiz_barcode_id.qty_available = self.product_qty_reserved
            self.wiz_barcode_id.product_id = self.product_id.id
            self.wiz_barcode_id.location_id = self.location_id.id
        self.wiz_barcode_id.with_context(manual_picking=True).action_confirm()

    def _get_fields_to_edit(self):
        return [
            "location_dest_id",
            "location_id",
            "product_id",
            "lot_id",
            "package_id",
        ]

    def action_barcode_inventory_quant_edit(self):
        wiz_barcode_id = self.env.context.get("wiz_barcode_id", False)
        wiz_barcode = self.env["wiz.stock.barcodes.read.picking"].browse(wiz_barcode_id)
        for quant in self:
            # Try to assign fields with the same name between quant and the scan wizard
            for fname in self._get_fields_to_edit():
                if hasattr(wiz_barcode, fname):
                    wiz_barcode[fname] = quant[fname]
            wiz_barcode.product_qty = quant.qty_done

        wiz_barcode.manual_entry = True
        self.env["bus.bus"]._sendone(
            "stock_barcodes_scan",
            "stock_barcodes_edit_manual",
            {
                "manual_entry": True,
            },
        )
