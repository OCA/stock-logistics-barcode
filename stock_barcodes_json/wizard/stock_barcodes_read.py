# Copyright 2019 Sergio Teruel <sergio.teruel@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import _, models
from odoo.tools.safe_eval import safe_eval


class WizStockBarcodesRead(models.AbstractModel):
    _inherit = "wiz.stock.barcodes.read"

    def process_barcode(self, barcode):

        try:
            safe_eval(barcode)
        except Exception:
            return super().process_barcode(barcode)

        barcode_decoded = safe_eval(self.barcode)

        if "product_id" in vals.keys():
            # Check if product exists
            self.product_id = vals["product_id"]
        if "product_barcode" in vals.keys():
            # Check if product exists, based on the product barcode
            product = self.env["product.product"].search(
                self._barcode_domain(vals["product_barcode"])
            )
            if not product:
                self._set_messagge_info("not_found", _("Barcode for product not found"))
                return False
            else:
                self.action_product_scaned_post(product)
        if "package_barcode" in vals.keys():
            # Search package
            packaging = self.env["product.packaging"].search(
                self._barcode_domain(vals["package_barcode"])
            )
            if not packaging:
                self._set_messagge_info(
                    "not_found", _("Barcode for product packaging not found")
                )
                return False
            else:
                if len(packaging) > 1:
                    self._set_messagge_info(
                        "more_match", _("More than one package found")
                    )
                    return False
                self.action_packaging_scaned_post(packaging)
        if "lot_barcode" in vals.keys():
            # Search lot based on barcode
            self.process_lot(vals["lot_barcode"])
        if "product_qty" in vals.keys():
            self.product_qty = vals["product_qty"]

        processed = True
        if processed:
            self.action_done()
            self._set_messagge_info("success", _("Barcode read correctly"))
            return True
        self._set_messagge_info("not_found", _("Barcode not found"))
        return False


class WizStockBarcodesMappingItem(models.Model):
    _name = "wiz.stock.barcodes.mapping.item"
    _description = "Barcode Item"
    _rec_name = "key"

    @api.model
    def _get_valid_fields(self):
        return [
            ("product_id", "Product"),
            ("product_qty", "Product Quantity"),
            ("product_barcode", "Product Barcode"),
            ("lot_barcode", "Lot Barcode"),
            ("package_barcode", "Package Barcode"),
        ]

    mapping_id = fields.Many2one("wiz.stock.barcodes.mapping")
    key = fields.Char(required=True)  # to do: selection to ir_fields
    value = fields.Selection(_get_valid_fields, required=True)


class WizStockBarcodesMapping(models.Model):
    _name = "wiz.stock.barcodes.mapping"
    _description = "Barcode Mapping"
    _rec_name = "model_id"

    model_id = fields.Many2one("ir.model", required=True)
    model_label_id = fields.Many2one(
        "ir.model", string="Model of the label", required=True
    )
    item_ids = fields.One2many(
        "wiz.stock.barcodes.mapping.item", "mapping_id", required=True
    )

    @api.model
    def prepare_label(self, model, items):
        json = "{"
        for item in items:
            json += "'{}': '{}',".format(item.key, item.value)
        json += "}"
        return {
            "name": "Label for " + model.name,
            "sequence": 32,
            "model_id": model.id,
            "component_ids": [
                (
                    0,
                    0,
                    {
                        "name": "QR json",
                        "component_type": "qr_code",
                        "magnification_factor": 5,
                        "data": json,
                    },
                )
            ],
        }

    @api.multi
    def create_zpl2_label(self):
        self.ensure_one()
        # here we will create zpl2 label with a json
        label_vals = self.prepare_label(self.model_label_id, self.item_ids)
        label = self.env["printing.label.zpl2"].create(label_vals)
        action = self.env.ref("printer_zpl2.act_open_printing_label_zpl2_view")
        action = action.read()[0]
        action["res_id"] = label.id
        return action
