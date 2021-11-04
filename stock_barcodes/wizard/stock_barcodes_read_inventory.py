# Copyright 2019 Sergio Teruel <sergio.teruel@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.fields import first


class WizStockBarcodesReadInventory(models.TransientModel):
    _name = "wiz.stock.barcodes.read.inventory"
    _inherit = "wiz.stock.barcodes.read"
    _description = "Wizard to read barcode on inventory"

    def _default_auto_lot(self):
        return self.env.user.company_id.stock_barcodes_inventory_auto_lot

    inventory_id = fields.Many2one(comodel_name="stock.inventory", readonly=True)
    inventory_product_qty = fields.Float(
        string="Inventory quantities", digits="Product Unit of Measure", readonly=True
    )
    auto_lot = fields.Boolean(
        string="Get lots automatically",
        help="If checked the lot will be set automatically with the same "
        "removal strategy",
        default=lambda self: self._default_auto_lot(),
    )

    def name_get(self):
        return [
            (
                rec.id,
                "{} - {} - {}".format(
                    _("Barcode reader"), rec.inventory_id.name, self.env.user.name
                ),
            )
            for rec in self
        ]

    def _prepare_inventory_line(self):
        return {
            "inventory_id": self.inventory_id.id,
            "product_id": self.product_id.id,
            "location_id": self.location_id.id,
            "product_uom_id": self.product_id.uom_id.id,
            "product_qty": self.product_qty,
            "prod_lot_id": self.lot_id.id,
        }

    def _prepare_inventory_line_domain(self, log_scan=False):
        """
        Use the same domain for create or update a stock inventory line.
        Source data is scanning log record if undo or wizard model if create or
        update one
        """
        record = log_scan or self
        return [
            ("inventory_id", "=", self.inventory_id.id),
            ("product_id", "=", record.product_id.id),
            ("location_id", "=", record.location_id.id),
            ("prod_lot_id", "=", record.lot_id.id),
        ]

    def _add_inventory_line(self):
        StockInventoryLine = self.env["stock.inventory.line"]
        line = StockInventoryLine.search(self._prepare_inventory_line_domain(), limit=1)
        if line:
            line.write({"product_qty": line.product_qty + self.product_qty})
        else:
            line = StockInventoryLine.create(self._prepare_inventory_line())
        self.inventory_product_qty = line.product_qty

    def check_done_conditions(self):
        if self.product_id.tracking != "none" and not self.lot_id and not self.auto_lot:
            self._set_messagge_info("info", _("Waiting for input lot"))
            return False
        return super().check_done_conditions()

    def action_done(self):
        result = super().action_done()
        if result:
            if self.auto_lot:
                self._distribute_inventory_lines()
            else:
                self._add_inventory_line()
        return result

    def action_manual_entry(self):
        result = super().action_manual_entry()
        if result:
            self.action_done()
        return result

    def reset_qty(self):
        super().reset_qty()
        self.inventory_product_qty = 0.0

    def action_undo_last_scan(self):
        res = super().action_undo_last_scan()
        log_scan = first(
            self.scan_log_ids.filtered(lambda x: x.create_uid == self.env.user)
        )
        if log_scan:
            inventory_line = self.env["stock.inventory.line"].search(
                self._prepare_inventory_line_domain(log_scan=log_scan)
            )
            if inventory_line.inventory_id.state == "done":
                raise ValidationError(
                    _(
                        "You can not remove a scanning log from an inventory "
                        "validated"
                    )
                )
            if inventory_line:
                qty = inventory_line.product_qty - log_scan.product_qty
                inventory_line.product_qty = max(qty, 0.0)
                self.inventory_product_qty = inventory_line.product_qty
        log_scan.unlink()
        return res

    def _distribute_inventory_lines(self):
        """Distribute the quantity to all quants.
        If the quantity is greater than all quant's quantities the difference
        will be assigned to last quant.
        """
        quants = self.env["stock.quant"]._gather(self.product_id, self.location_id)
        # If the product changed from untracked to tracked we need to avoid to
        # distribute quantities to possible quants with no lot, as those should
        # be corrected with the inventory. For example with remanent negative
        # quants.
        if self.product_id.tracking != "none":
            quants = quants.filtered("lot_id")
        if not quants:
            self._set_messagge_info(
                "not_found", _("There is no lots to assign quantities")
            )
            return False
        qty_to_assign = self.product_qty
        for quant in quants:
            qty = (
                qty_to_assign
                if qty_to_assign <= quant.quantity
                else max(quant.quantity, 0)
            )
            self.with_context(keep_auto_lot=True).lot_id = quant.lot_id
            self.product_qty = qty if qty > 0.0 else 0.0
            self._add_inventory_line()
            qty_to_assign -= qty
        if qty_to_assign:
            self.with_context(keep_auto_lot=True).lot_id = quants[-1:].lot_id
            self.product_qty = qty_to_assign
            self._add_inventory_line()

    @api.onchange("product_id")
    def _onchange_product_id(self):
        self.lot_id = False
        self.auto_lot = self._default_auto_lot()

    @api.onchange("lot_id")
    def _onchange_lot_id(self):
        if self.lot_id and not self.env.context.get("keep_auto_lot"):
            self.auto_lot = False

    @api.onchange("manual_entry")
    def _onchange_manual_entry(self):
        self.auto_lot = self._default_auto_lot()
