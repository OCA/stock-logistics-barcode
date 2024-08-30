# Copyright 2019 Sergio Teruel <sergio.teruel@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class WizStockBarcodesReadTodo(models.TransientModel):
    _name = "wiz.stock.barcodes.read.todo"
    _description = "Wizard to read barcode todo"

    # To prevent remove the record wizard until 2 days old
    _transient_max_hours = 48

    name = fields.Char()
    wiz_barcode_id = fields.Many2one(comodel_name="wiz.stock.barcodes.read.picking")
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
    location_id = fields.Many2one(comodel_name="stock.location")
    location_name = fields.Char(related="location_id.name")
    location_dest_id = fields.Many2one(comodel_name="stock.location")
    location_dest_name = fields.Char(
        string="Destinatino Name", related="location_dest_id.name"
    )
    product_id = fields.Many2one(comodel_name="product.product")
    lot_id = fields.Many2one(comodel_name="stock.production.lot")
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

    def action_todo_next(self):
        self.state = "done_forced"
        self.line_ids.barcode_scan_state = "done_forced"
        self.wiz_barcode_id.determine_todo_action()

    def action_reset_lines(self):
        self.state = "pending"
        self.line_ids.barcode_scan_state = "pending"
        self.line_ids.qty_done = 0.0
        self.wiz_barcode_id.action_clean_values()
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
        "line_ids.product_uom_qty",
        "line_ids.barcode_scan_state",
        "qty_done",
        "product_uom_qty",
    )
    def _compute_state(self):
        for rec in self:
            if rec.qty_done >= rec.product_uom_qty or (
                rec.wiz_barcode_id.option_group_id.source_pending_moves
                == "move_line_ids"
                and rec.line_ids
                and not any(ln.barcode_scan_state == "pending" for ln in rec.line_ids)
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
