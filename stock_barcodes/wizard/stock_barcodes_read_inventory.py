# Copyright 2023 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import _, api, fields, models


class WizStockBarcodesReadInventory(models.TransientModel):
    _name = "wiz.stock.barcodes.read.inventory"
    _inherit = "wiz.stock.barcodes.read"
    _description = "Wizard to read barcode on inventory"
    _allowed_product_types = ["consu"]

    def _get_product_domain(self):
        return [("type", "in", self._allowed_product_types), ("is_storable", "=", True)]

    # Overwrite is needed to take into account new domain values
    product_id = fields.Many2one(domain=_get_product_domain)
    inventory_product_qty = fields.Float(
        string="Inventory quantities", digits="Product Unit of Measure", readonly=True
    )
    inventory_quant_ids = fields.Many2many(
        comodel_name="stock.quant", compute="_compute_inventory_quant_ids"
    )
    count_inventory_quants = fields.Integer(
        compute="_compute_count_inventory_quants", store=True
    )
    display_read_quant = fields.Boolean(string="Read items", default=True)

    def action_display_read_quant(self):
        self.display_read_quant = not self.display_read_quant
        self._refresh_inventory_quants()

    @api.depends("inventory_quant_ids")
    def _compute_count_inventory_quants(self):
        for wiz in self:
            wiz.count_inventory_quants = len(wiz.inventory_quant_ids)

    def _inventory_quant_ids_domain(self):
        """Domain to retrieve the quants shown on the inventory mode list."""
        self.ensure_one()
        domain = [
            ("user_id", "=", self.env.user.id),
            ("inventory_date", "<=", fields.Date.context_today(self)),
        ]
        if self.display_read_quant:
            domain.append(("inventory_quantity_set", "=", True))
        else:
            domain.append(("inventory_quantity_set", "=", False))
        return domain

    def _search_inventory_quants(self):
        """Return the quants to display, ordered by write date when showing the
        already read items or by location otherwise."""
        self.ensure_one()
        order = "write_date DESC" if self.display_read_quant else None
        quants = self.env["stock.quant"].search(
            self._inventory_quant_ids_domain(), order=order
        )
        if order is None:
            quants = quants.sorted(
                lambda q: (
                    q.location_id.posx,
                    q.location_id.posy,
                    q.location_id.posz,
                    q.location_id.name,
                )
            )
        return quants

    @api.depends("display_read_quant")
    def _compute_inventory_quant_ids(self):
        # Keep this compute side-effect free: record writes and bus
        # notifications are handled by _refresh_inventory_quants.
        for wiz in self:
            wiz.inventory_quant_ids = wiz._search_inventory_quants()

    def _refresh_inventory_quants(self):
        """Stamp the selected owner on the displayed quants (when enabled) and
        notify the client to refresh the apply-inventory counter.

        These side effects are intentionally kept out of the compute method so
        they are not triggered on every recomputation.
        """
        for wiz in self:
            if wiz.show_owner and wiz.owner_id:
                wiz.inventory_quant_ids.with_context(allow_edit_owner=True).write(
                    {"owner_id": wiz.owner_id.id}
                )
            wiz.send_bus_done(
                "stock_barcodes_form_update",
                {
                    "type": "count_apply_inventory",
                    "payload": {"count": wiz.count_inventory_quants},
                },
            )

    def _prepare_stock_quant_values(self):
        return {
            "product_id": self.product_id.id,
            "location_id": self.location_id.id,
            "inventory_quantity": self.product_qty,
            "lot_id": self.lot_id.id,
            "package_id": self.package_id.id,
        }

    def _inventory_quant_domain(self):
        return [
            ("user_id", "=", self.env.user.id),
            (
                "inventory_date",
                "<=",
                fields.Date.context_today(self).strftime("%Y-%m-%d"),
            ),
            ("product_id", "=", self.product_id.id),
            ("location_id", "=", self.location_id.id),
            ("lot_id", "=", self.lot_id.id),
            ("package_id", "=", self.package_id.id),
        ]

    def _add_inventory_quant(self):
        StockQuant = self.env["stock.quant"]
        quant = StockQuant.search(self._inventory_quant_domain(), limit=1)
        quant = quant.with_context(inventory_mode=True)
        if quant:
            if self.product_id.tracking == "serial" and (
                quant.inventory_quantity > 0.0 or self.product_qty != 1
            ):
                self._serial_tracking_message_fail()
                return False
            if self.option_group_id.accumulate_read_quantity:
                quant.inventory_quantity += self.product_qty
            else:
                quant.inventory_quantity = self.product_qty
        else:
            if self.product_id.tracking == "serial" and self.product_qty != 1:
                self._serial_tracking_message_fail()
                return False
            quant = StockQuant.with_context(inventory_mode=True).create(
                self._prepare_stock_quant_values()
            )
        self.inventory_product_qty = quant.quantity
        return True

    def _serial_tracking_message_fail(self):
        self._set_message_info(
            "more_match",
            _("Inventory line with more than one unit in serial tracked product"),
        )

    def action_done(self):
        result = super().action_done()
        if result:
            result = self._add_inventory_quant()
            if result:
                self.action_clean_values()
        return result

    def action_manual_entry(self):
        result = super().action_manual_entry()
        if result:
            self.action_done()
        return result

    def action_clean_values(self):
        res = super().action_clean_values()
        self.inventory_product_qty = 0.0
        self.package_id = False
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

    @api.onchange("product_id")
    def _onchange_product_id(self):
        if self.product_id != self.lot_id.product_id:
            self.lot_id = False

    @api.onchange("lot_id")
    def _onchange_lot_id(self):
        if self.lot_id and not self.env.context.get("keep_auto_lot"):
            self.auto_lot = False

    def apply_inventory(self):
        action = self.env["ir.actions.actions"]._for_xml_id(
            "stock.action_stock_inventory_adjustement_name"
        )
        action["context"] = {"default_quant_ids": self.inventory_quant_ids.ids}
        return action
