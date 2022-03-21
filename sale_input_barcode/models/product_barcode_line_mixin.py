# copyright 2022 David BEAL @ Akretion

from odoo import _, models
from odoo.exceptions import UserError


class ProductLineMixin(models.AbstractModel):
    _name = "product.barcode.line.mixin"
    _description = "Utilities for any model to deal with product_id field"

    def _process_barcode_on_product_line(self, barcode):
        """
        This mixin may be moved in another module to be used in mixed use cases
        res =>
        {
            "01": "03400933816759",  # GTIN
            "17": "2014-05-31",      # expiry date
            "10": "B04059A",         # lot number
            "310": 0.06385,          # weight
            "15": "2014-05-01",      # sale date
        }
        """
        res = self.env["gs1_barcode"].decode(barcode)
        if not res.get("01"):
            raise UserError(
                _(
                    "Decoded barcode %s doesn't include a valid segment for GTIN"
                    % barcode
                )
            )
        product = self.env["product.product"].search([("barcode", "=", res["01"])])
        if product:
            if len(product) > 1:
                raise UserError(
                    _(
                        "These products %s share the same barcode.\n"
                        "Impossible to guess which one to choose."
                        % [(x.display_name for x in product)]
                    )
                )
        else:
            raise UserError(_("No product found matching this barcode %s" % barcode))
        vals = {"product_id": product.id}
        if res.get("10") and "lot_id" in self._fields:
            # some module may add `lot_id` field
            # like sale_order_lot_selection (sale-workflow)
            lot = self.env["stock.production.lot"].search(
                [("name", "=", res["10"]), ("product_id", "=", product.id)]
            )
            if not lot:
                lot = self._create_unknown_lot(barcode, res, product)
            if lot:
                # _create_unknown_lot may be overriden to not return lot
                vals["lot_id"] = lot.id
        if "order_id" in self._fields:
            vals["order_id"] = self.env.context.get("order_id")
        self.create(vals)

    def _create_unknown_lot(self, barcode, barcode_infos, product):
        """Inherit to implement your own scenario creation
        i.e.
        raise UserError(_("No lot found matching this barcode %s" % barcode))
            or
        return False
        """
        company_id = self.env.context.get("company_id") or self.env.user.company_id.id
        lot_vals = {
            "name": barcode_infos["10"],
            "expiry_date": barcode_infos["17"],
            "product_id": product.id,
            "company_id": company_id,
        }
        return self.env["stock.production.lot"].create(lot_vals)
