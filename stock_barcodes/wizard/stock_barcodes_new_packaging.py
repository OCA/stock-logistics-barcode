# Copyright 2026 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import fields, models
from odoo.exceptions import ValidationError
from odoo.tools.float_utils import float_compare


class WizStockBarcodesNewPackaging(models.TransientModel):
    _inherit = "barcodes.barcode_events_mixin"
    _name = "wiz.stock.barcodes.new.packaging"
    _description = "Wizard to create new product packaging from barcode scanner"

    product_id = fields.Many2one(comodel_name="product.product", required=True)
    barcode = fields.Char(required=True)
    name = fields.Char(required=True)
    quantity = fields.Float(
        string="Contains", default=1.0, required=True, digits="Product Unit"
    )

    def on_barcode_scanned(self, barcode):
        self.barcode = barcode
        self.name = barcode

    def _prepare_uom_values(self):
        return {
            "name": self.name,
            "relative_uom_id": self.product_id.uom_id.id,
            "relative_factor": self.quantity,
        }

    def _get_existing_uom(self, Uom):
        """Return a UoM with the same size, preferring the product's packagings,
        so scanning a new barcode for a known size does not duplicate it."""
        reference = self.product_id.uom_id
        precision = self.env["decimal.precision"].precision_get("Product Unit")
        candidates = self.product_id.uom_ids | Uom.search(
            [("relative_uom_id", "=", reference.id)]
        )
        return candidates.filtered(
            lambda uom: uom.relative_uom_id == reference
            and not float_compare(
                uom.relative_factor, self.quantity, precision_digits=precision
            )
        )[:1]

    def _prepare_product_uom_values(self, uom):
        return {
            "product_id": self.product_id.id,
            "uom_id": uom.id,
            "barcode": self.barcode,
            "company_id": self.product_id.company_id.id or self.env.company.id,
        }

    def get_scan_wizard(self):
        return self.env[self.env.context["active_model"]].browse(
            self.env.context["active_id"]
        )

    def scan_wizard_action(self):
        if self.env.context.get("active_model") == "wiz.stock.barcodes.read.inventory":
            action = self.env["ir.actions.actions"]._for_xml_id(
                "stock_barcodes.action_stock_barcodes_read_inventory"
            )
        else:
            action = self.env["ir.actions.actions"]._for_xml_id(
                "stock_barcodes.action_stock_barcodes_read_picking"
            )
        action["res_id"] = self.get_scan_wizard().id
        return action

    def confirm(self):
        self.ensure_one()
        if self.quantity <= 0:
            raise ValidationError(self.env._("Packaging quantity must be positive."))
        packaging = self.env["product.uom"].search(
            [("barcode", "=", self.barcode)], limit=1
        )
        if packaging and packaging.product_id != self.product_id:
            raise ValidationError(
                self.env._("This barcode is already used by another product.")
            )
        if not packaging:
            # Odoo 18 granted Inventory administrators full access to
            # product.packaging. Odoo 19 stores packaging barcodes in product.uom
            # and the packaging size in uom.uom; those records are normally
            # writable by Product administrators. Preserve the former Inventory
            # administrator capability without broadening the global UoM ACLs.
            is_stock_manager = self.env.user.has_group("stock.group_stock_manager")
            Uom = (
                self.env["uom.uom"].sudo() if is_stock_manager else self.env["uom.uom"]
            )
            ProductUom = (
                self.env["product.uom"].sudo()
                if is_stock_manager
                else self.env["product.uom"]
            )
            product = self.product_id.sudo() if is_stock_manager else self.product_id
            uom = self._get_existing_uom(Uom) or Uom.create(self._prepare_uom_values())
            if uom not in product.uom_ids:
                product.uom_ids |= uom
            packaging = ProductUom.create(self._prepare_product_uom_values(uom))
        wiz = self.get_scan_wizard()
        if wiz:
            wiz.packaging_uom_id = packaging.uom_id
        return self.scan_wizard_action()

    def cancel(self):
        return self.scan_wizard_action()
