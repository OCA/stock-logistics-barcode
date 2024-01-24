# Copyright 2017 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import json

from lxml import etree

from odoo import api, models


class StockLocation(models.Model):
    _name = "stock.location"
    _description = "Stock Location"
    _inherit = ["stock.location", "barcode.generate.mixin"]

    @api.model
    def get_view(self, view_id=None, view_type="form", **options):
        """The redefinition of this method is intended to manipulating
        the form view of stock.location to add the barcode field to the
        view in case it has not been added by the stock_barcodes module.
        """
        result = super().get_view(view_id=view_id, view_type=view_type, **options)
        if view_type == "form":
            doc = etree.XML(result["arch"])
            barcode_field = doc.xpath("//field[@name='barcode']")
            if barcode_field:
                # If the field exists in the view, it's assumed it has
                # been added by 'stock_barcodes' module, then all the
                # fields inside 'barcodes_generator_location' group
                # (added by this module) are moved next to the existing
                # `barcode' field.
                barcode_field = barcode_field[0]
                group = doc.xpath("//group[@name='barcodes_generator_location']")[0]
                for node in group.getchildren()[::-1]:
                    barcode_field.addnext(node)
                # Remove the group since it will be empty at this point.
                group.getparent().remove(group)
            else:
                # If the field does not exist in the view, it is added
                # together with the fields that this module adds.
                barcode_field = etree.Element("field", {"name": "barcode"})
                placeholder = doc.xpath("//field[@name='barcode_rule_id']")[0]
                placeholder.addprevious(barcode_field)
            # To the `barcode` field in the view (either the new
            # or the existing one), a modifier is added.
            modifier = {"readonly": [("generate_type", "=", "sequence")]}
            barcode_field.set("modifiers", json.dumps(modifier))
            result["arch"] = etree.tostring(doc)
        return result
