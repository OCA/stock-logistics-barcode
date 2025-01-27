# Copyright 2019 Sergio Teruel <sergio.teruel@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).f
from odoo import api, fields, models


class WizCandidatePicking(models.TransientModel):

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
                candidate.picking_id.mapped("move_ids.reserved_availability")
            )
            for move in candidate.picking_id.move_ids:
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
        context = dict(self.env.context)
        picking = self._get_picking_to_validate()
        if picking._check_immediate():
            return False, picking.with_context(
                button_validate_picking_ids=picking.ids, operations_mode=True
            )._action_generate_immediate_wizard(
                show_transfers=picking._should_show_transfers()
            )
        return (
            True,
            picking.with_context(
                skip_sms=context.get("skip_sms", False)
            ).button_validate(),
        )

    def action_open_picking(self):
        picking = self.env["stock.picking"].browse(
            self.env.context.get("picking_id", False)
        )
        return picking.with_context(control_panel_hidden=False).get_formview_action()

    def action_put_in_pack(self):
        self.picking_id.action_put_in_pack()
