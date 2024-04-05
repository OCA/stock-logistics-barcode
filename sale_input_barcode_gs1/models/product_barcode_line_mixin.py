# copyright 2022 David BEAL @ Akretion

from odoo import _, api, models
from odoo.exceptions import UserError


class ProductLineMixin(models.AbstractModel):
    _inherit = "product.barcode.line.mixin"

    @api.model
    def _decode_barcode(self, raw_barcode):
        """
        res =>
        {
            "01": "03400933816759",  # GTIN
            "17": "2014-05-31",      # expiry date
            "10": "B04059A",         # lot number
            "310": 0.06385,          # weight
            "15": "2014-05-01",      # sale date
        }
        """
        raw_barcode, barcode_dict = super()._decode_barcode(raw_barcode)
        barcode_dict = self.env["gs1_barcode"].decode(raw_barcode)
        if not barcode_dict.get("01"):
            raise UserError(
                _(
                    "Decoded barcode %s doesn't include a valid segment for GTIN"
                    % barcode_dict
                )
            )
        return barcode_dict["01"], barcode_dict

    def _populate_vals(self, product, barcode_dict):
        vals = super()._populate_vals(product, barcode_dict)
        if barcode_dict.get("10") and "lot_id" in self._fields:
            # some module may add `lot_id` field
            # like sale_order_lot_selection (sale-workflow)
            lot = self.env["stock.production.lot"].search(
                [("name", "=", barcode_dict["10"]), ("product_id", "=", product.id)]
            )
            if not lot:
                lot = self._create_unknown_lot(barcode_dict, product)
            if lot:
                # _create_unknown_lot may be overriden to not return lot
                vals["lot_id"] = lot.id
        return vals

    def _create_unknown_lot(self, barcode_dict, product):
        """Inherit to implement your own scenario creation
        i.e.
        raise UserError(_("No lot found matching this barcode %s" % barcode))
            or
        return False
        """
        company_id = self.env.context.get("company_id") or self.env.company.id
        lot_vals = {
            "name": barcode_dict["10"],
            "expiry_date": barcode_dict["17"],
            "product_id": product.id,
            "company_id": company_id,
        }
        return self.env["stock.production.lot"].create(lot_vals)
