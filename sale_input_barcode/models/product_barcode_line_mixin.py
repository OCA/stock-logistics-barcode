# copyright 2022 David BEAL @ Akretion

from odoo import api, models
from odoo.exceptions import UserError


class ProductLineMixin(models.AbstractModel):
    """This mixin may be moved in another module to be used in mixed use cases"""

    _name = "product.barcode.line.mixin"
    _description = "Utilities for any model to deal with product_id field"

    @api.model
    def _decode_barcode(self, raw_barcode):
        """
        Return the barcode as a simple string,
        and optionally a dictionary containing more info
        deduced from the barcode itself.

        Hook for customizations, see sale_input_barcode_gs1
        """
        return raw_barcode, None

    def _populate_vals(self, product, barcode_dict):
        """
        Builds a dictionary to use in the `create` function
        Hook for customizations
        """
        return {
            "product_id": product.id,
            "product_uom_qty": 1,
        }

    def _process_barcode_on_product_line(self, raw_barcode):
        barcode_str, barcode_dict = self._decode_barcode(raw_barcode)
        product = self.env["product.product"].search([("barcode", "=", barcode_str)])
        if product:
            if len(product) > 1:
                raise UserError(
                    self.env._(
                        "These products %s share the same barcode.\n"
                        "Impossible to guess which one to choose.",
                        ", ".join(product.mapped("display_name")),
                    )
                )
        else:
            raise UserError(
                self.env._("No product found matching this barcode %s", barcode_str)
            )

        return self._populate_vals(product, barcode_dict)
