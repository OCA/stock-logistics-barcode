# Copyright 2015-2021 Akretion (http://www.akretion.com)
# @author Alexis de Lattre <alexis.delattre@akretion.com>
# Copyright 2025 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import Command, api, fields, models
from odoo.exceptions import UserError
from odoo.tools import float_compare, float_is_zero


class StockInventoryBarcode(models.TransientModel):
    _name = "stock.inventory.barcode"
    _description = "Stock Inventory Barcode Wizard"

    inventory_id = fields.Many2one("stock.inventory", string="Inventory", required=True)
    company_id = fields.Many2one("res.company", string="Company", required=True)
    product_code = fields.Char(
        string="Barcode or Internal Reference",
        help="This field is designed to be filled with a barcode reader",
    )
    product_id = fields.Many2one(
        "product.product",
        string="Product",
        required=True,
    )
    uom_name = fields.Char(related="product_id.uom_id.name")
    location_id = fields.Many2one(
        "stock.location",
        string="Location",
        required=True,
    )
    multi_stock_location = fields.Boolean(readonly=True)
    lot_id = fields.Many2one(
        "stock.lot",
        string="Lot",
        domain="[('product_id', '=', product_id), ('company_id', '=', company_id)]",
    )
    product_tracking = fields.Selection(
        [
            ("serial", "By Unique Serial Number"),
            ("lot", "By Lots"),
            ("none", "No Tracking"),
        ],
        string="Tracking",
        required=True,
    )
    note = fields.Text()
    quant_id = fields.Many2one(
        "stock.quant",
    )
    theoretical_qty = fields.Float(related="quant_id.quantity", readonly=True)
    product_qty = fields.Float(
        string="Current Real Quantity",
        related="quant_id.inventory_quantity",
        readonly=True,
    )
    zero_count = fields.Boolean(default=1)
    auto_save = fields.Boolean(default=1)
    change_qty = fields.Float(
        string="Change Real Quantity", digits="Product Unit of Measure"
    )
    add_qty = fields.Float(
        string="Add to Real Quantity", digits="Product Unit of Measure"
    )

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        assert self._context.get("active_model") == "stock.inventory"
        inv = self.env["stock.inventory"].browse(self._context.get("active_id"))
        if inv.state != "in_progress":
            raise UserError(
                self.env._(
                    "You cannot start the barcode interface on inventory '%s' "
                    "which is not 'In Progress'."
                )
                % inv.display_name
            )
        res["inventory_id"] = inv.id
        res["company_id"] = inv.company_id.id
        if inv.location_ids:
            loc_domain = [("id", "child_of", inv.location_ids.ids)]
        else:
            loc_domain = [
                ("company_id", "=", inv.company_id.id),
                ("usage", "in", ("internal", "transit")),
            ]
        inv_locations = self.env["stock.location"].search(loc_domain)
        if len(inv_locations) > 1:
            res["multi_stock_location"] = True
        elif len(inv_locations) == 1:
            res["multi_stock_location"] = False
            res["location_id"] = inv_locations.id
        else:
            raise UserError(self.env._("No internal/transit stock locations."))
        return res

    @api.onchange("product_code")
    def product_code_change(self):
        if self.product_code:
            product = self.env["product.product"].search(
                [
                    ("barcode", "=", self.product_code),
                    ("is_storable", "=", True),
                ]
            )
            if not product:
                product = self.env["product.product"].search(
                    [
                        ("default_code", "=ilike", self.product_code),
                        ("is_storable", "=", True),
                    ]
                )
            if len(product) == 1:
                self.product_id = product
                if product:
                    self.product_code = False
                if (
                    self.zero_count
                    and self.quant_id
                    and self.product_id == self.quant_id.product_id
                    and self.lot_id == self.quant_id.lot_id
                    and self.location_id == self.quant_id.location_id
                ):
                    self.add_qty += 1
            elif len(product) > 1:
                return {
                    "warning": {
                        "title": self.env._("Error"),
                        "message": self.env._(
                            "Several stockable products have been found "
                            "with this code as Internal Reference:\n %s"
                            "\nYou should select the right product manually."
                        )
                        % "\n".join([p.display_name for p in product]),
                    }
                }
            else:
                return {
                    "warning": {
                        "title": self.env._("Error"),
                        "message": self.env._(
                            "No stockable product found with this code as "
                            "Barcode nor Internal Reference. You should select "
                            "the right product manually."
                        ),
                    }
                }

    @api.onchange("product_id")
    def product_id_change(self):
        if (
            self.auto_save
            and self.quant_id
            and self.product_id != self.quant_id.product_id
        ):
            self.save()
        if self.product_id:
            self.product_tracking = self.product_id.tracking
            if not self.product_tracking or self.product_tracking == "none":
                self.lot_id = False
            self._set_location()
        else:
            self.product_tracking = False
            self.lot_id = False
            self.note = False

    def _set_location(self):
        location = self.inventory_id.location_ids
        if len(location) != 1:
            return
        self.location_id = location._get_putaway_strategy(self.product_id)

    @api.onchange("product_id", "location_id", "lot_id")
    def product_lot_loc_change(self):
        res = {"warning": {}}
        if self.product_id and self.location_id:
            if not self.product_id.tracking or self.product_id.tracking == "none":
                if self.lot_id:
                    raise UserError(
                        self.env._(
                            "Product '%s' is not tracked by lot/serial so the "
                            "lot field must be empty. This should never "
                            "happen."
                        )
                        % self.product_id.display_name
                    )
                self.update_wiz_screen(res)
            elif self.lot_id:
                self.update_wiz_screen(res)
        return res

    def update_wiz_screen(self, res):
        if (
            self.zero_count
            and self.quant_id
            and self.product_id == self.quant_id.product_id
            and self.lot_id == self.quant_id.lot_id
            and self.location_id == self.quant_id.location_id
        ):
            return

        locations = self.inventory_id.location_ids or self.location_id
        product_quants = self.inventory_id.stock_quant_ids.filtered_domain(
            [
                ("product_id", "=", self.product_id.id),
                ("location_id", "child_of", locations.ids),
            ]
        )
        quant = product_quants.filtered(
            lambda q: q.location_id == self.location_id and q.lot_id == self.lot_id
        )
        if len(quant) > 1:
            res["warning"] = {
                "title": self.env._("Error"),
                "message": self.env._(
                    "Several inventory lines exists for this product "
                    "(and lot) on the same stock location. "
                    "This should happen only when using packaging, "
                    "but this scenario is not supported for the moment."
                ),
            }
            quant = quant[0]
        if not quant:
            quant = self.env["stock.quant"].create(
                {
                    "product_id": self.product_id.id,
                    "lot_id": self.lot_id and self.lot_id.id or False,
                    "location_id": self.location_id.id,
                    "inventory_quantity": 0,
                    "current_inventory_id": self.inventory_id.id,
                    "stock_inventory_ids": [Command.link(self.inventory_id.id)],
                }
            )

        other_quants = product_quants - quant
        other_quants.filtered(
            lambda q: not q.inventory_quantity_set
        ).inventory_quantity = 0
        self.quant_id = quant
        self.add_qty = 1

        self.change_qty = self.product_qty

        quants_same_product = other_quants.filtered("inventory_quantity")
        note_list = []
        tracking = self.product_id.tracking in ("lot", "serial") and True or False
        for q in quants_same_product:
            if tracking:
                note_list.append(
                    self.env._("Lot %s already inventoried on %s with real qty %.3f %s")
                    % (
                        q.lot_id and q._lot_id.display_name or self.env._("<none>"),
                        q.location_id.display_name,
                        q.inventory_quantity,
                        self.uom_name,
                    )
                )
            else:
                note_list.append(
                    self.env._("Already inventoried on %s with real qty %.3f %s")
                    % (q.location_id.display_name, q.inventory_quantity, self.uom_name)
                )
        if note_list:
            note = "\n".join(note_list)
            self.note = note
        else:
            self.note = False

    def save(self):
        self.ensure_one()
        if not self.quant_id:
            raise UserError(self.env._("No related quant"))
        if self.inventory_id.state != "in_progress":
            raise UserError(
                self.env._("The inventory '%s' is not 'In Progress' any more.")
                % self.inventory_id.display_name
            )
        prec = self.env["decimal.precision"].precision_get("Product Unit of Measure")
        if self.zero_count and not float_is_zero(self.add_qty, precision_digits=prec):
            self.quant_id.inventory_quantity += self.add_qty
        elif not self.zero_count and float_compare(
            self.change_qty, self.product_qty, precision_digits=prec
        ):
            self.quant_id.inventory_quantity = self.change_qty
        action = {
            "name": self.env._("Stock Inventory Barcode Wizard"),
            "type": "ir.actions.act_window",
            "res_model": "stock.inventory.barcode",
            "view_mode": "form",
            "nodestroy": True,
            "target": "new",
            "context": self._context,
        }
        return action
