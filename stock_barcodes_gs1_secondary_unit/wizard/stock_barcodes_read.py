# Copyright 2019 Sergio Teruel <sergio.teruel@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import _, api, fields, models


class WizStockBarcodesRead(models.AbstractModel):
    _inherit = "wiz.stock.barcodes.read"

    product_tmpl_id = fields.Many2one(
        comodel_name="product.template",
        related="product_id.product_tmpl_id",
    )
    secondary_uom_id = fields.Many2one(
        comodel_name="product.secondary.unit",
        string="Secondary uom",
    )
    secondary_uom_qty = fields.Float(
        string="Secondary UOM Qty", digits="Product Unit of Measure"
    )
    secondary_single_qty = fields.Float(
        string="Secondary single Qty", digits="Product Unit of Measure"
    )
    total_secondary_uom_qty = fields.Float(
        string="Second. Demand", digits="Product Unit of Measure", store=False
    )
    total_secondary_uom_qty_done = fields.Float(
        string="Second. Done", digits="Product Unit of Measure", store=False
    )
    gs1_qty_target_field = fields.Selection(
        selection=[("secondary_uom_qty", "Secondary unit qty")],
        help="Technical field to establish which quantity field a GS1 count "
        "AI (30 - Variable count of items, 37 - Count of items) should be "
        "routed to, set by AI 02 matching a secondary unit package.",
    )

    @api.onchange("secondary_uom_id", "secondary_uom_qty", "secondary_single_qty")
    def onchange_secondary_uom_qty(self):
        self.product_qty = (
            self.secondary_uom_qty * self.secondary_uom_id.factor
        ) + self.secondary_single_qty

    def action_secondary_uom_scaned_post(self, secondary_uom):
        self.secondary_uom_id = secondary_uom
        if self.product_id != secondary_uom.product_tmpl_id.product_variant_id:
            self.lot_id = False
        self.product_id = secondary_uom.product_tmpl_id.product_variant_id
        if self.manual_entry or self.is_manual_qty:
            return
        elif self.secondary_uom_id:
            self.secondary_uom_qty = 1.0
            self.product_qty = self.secondary_uom_id.factor * self.secondary_uom_qty
        else:
            self.secondary_uom_qty = 0.0
            self.product_qty = 1.0

    def reset_qty(self):
        res = super().reset_qty()
        self.secondary_uom_qty = 0
        return res

    def _process_ai_01(self, gs1_list):
        secondary_uom = self.env["product.secondary.unit"].search(
            self._barcode_domain(self.barcode)
        )
        if not secondary_uom:
            return super()._process_ai_01(gs1_list)
        else:
            if len(secondary_uom) > 1:
                self._set_messagge_info(
                    "more_match", _("More than one secondary uom found")
                )
                return False
            self.action_secondary_uom_scaned_post(secondary_uom)
        return True

    def _process_ai_02(self, gs1_list):
        secondary_uom = self.env["product.secondary.unit"].search(
            self._barcode_domain(self.barcode)
        )
        if not secondary_uom:
            self.gs1_qty_target_field = False
            return super()._process_ai_02(gs1_list)
        else:
            if len(secondary_uom) > 1:
                self._set_messagge_info(
                    "more_match", _("More than one secondary uom found")
                )
                return False
            self.gs1_qty_target_field = "secondary_uom_qty"
            self.action_secondary_uom_scaned_post(secondary_uom)
        return True

    def _set_gs1_product_qty(self, product_qty):
        """AI 30 (Variable count of items) and AI 37 (Count of items) both
        route through this shared hook in the base module. When AI 02
        identified a secondary-unit package above, the count belongs to
        the secondary unit (e.g. pieces), not the primary quantity (e.g.
        weight) the base module would otherwise set it to - covering both
        AIs the same way the base module itself unifies them, instead of
        only overriding AI 37.
        """
        if self.gs1_qty_target_field != "secondary_uom_qty":
            return super()._set_gs1_product_qty(product_qty)
        self.secondary_uom_qty = product_qty
        self.onchange_secondary_uom_qty()
        return True

    @api.onchange("product_id")
    def onchange_product_id(self):
        res = super().onchange_product_id()
        self.secondary_uom_id = self.product_id.stock_secondary_uom_id
        return res

    def _set_focus_on_qty_input(self, field_name=None):
        if field_name is None and self.secondary_uom_id:
            field_name = "secondary_uom_qty"
        return super()._set_focus_on_qty_input(field_name=field_name)

    def action_clean_values(self):
        res = super().action_clean_values()
        self.secondary_uom_qty = 0.0
        self.secondary_single_qty = 0.0
        self.gs1_qty_target_field = False
        return res
