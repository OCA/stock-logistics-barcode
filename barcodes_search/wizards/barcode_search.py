# coding: utf-8
# Copyright (C) 2017-Today GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class BarcodeSearch(models.TransientModel):
    _name = "barcode.search"
    _description = "Barcode Search"

    barcode = fields.Char(
        string="Barcode to Search",
        required=True,
    )

    state = fields.Selection(
        selection=[("new", "New"), ("done", "Done")],
        default="new")

    line_ids = fields.One2many(
        comodel_name="barcode.search.line",
        inverse_name="barcode_search_id",
        readonly=True)

    @api.multi
    def action_search(self):
        self.ensure_one()
        res = self.search_by_barcode(self.barcode)
        if len(res) == 1 and not res[0]["extra_data"]:
            # Display the result in the according form view
            return res[0]["record"].get_formview_action()
        else:
            # Update Wizard Values
            line_vals = [(5, 0)]
            for item in res:
                line_vals.append((0, 0, {
                    "field_id": item["field"].id,
                    "item_ref": item["record"].id,
                    "item_name": item["record"].name,
                    "extra_data": item["extra_data"],
                }))
            self.write({
                "state": "done",
                "line_ids": line_vals,
            })

            # Return Action
            action = self.get_formview_action()
            action["target"] = "new"
            return action

    @api.model
    def search_by_barcode(self, barcode):
        """Return a list of dict that matches with the given barcode
        with the following format
        [{"field": field, "record": record, "extra_data": extra_data_dict)
        """
        barcode_fields = self.get_barcode_fields()
        res = self._search_by_barcode_barcode_fields(
            barcode, barcode_fields
        )

        # Extra search for objects that have a barcode with encoded data
        # Typical exemple, product with a pattern 20{barcode_base}{NNDDD}
        # where {NNDDD} is the weight of the product
        nomenclature_obj = self.env["barcode.nomenclature"]
        nomenclatures = nomenclature_obj.search([])
        rule_types = self.get_model_by_rule_type()
        for nomenclature in nomenclatures:
            parsed_result = nomenclature.parse_barcode(barcode)
            rule_type = parsed_result["type"]
            if rule_type in rule_types:
                barcode_fields = self.get_barcode_fields(rule_types[rule_type])
                base_code = parsed_result["base_code"]
                extra_results = self._search_by_barcode_barcode_fields(
                    base_code, barcode_fields
                )
                for extra_result in extra_results:
                    extra_result["extra_data"].update({
                        "type":  rule_type,
                        "value": parsed_result["value"],
                    })
                res += extra_results
        return res

    @api.model
    def get_barcode_fields(self, model_name=False):
        """Return a recordset of fields that represent a barcode, in any model.

        By default, it will return all fields named "barcode".
        Note : Overload that function in a custom module, if you define
        a barcode field with a name different than "barcode"."""
        IrModelFields = self.env["ir.model.fields"]

        domain = [
            ('name', '=', 'barcode'), ('model', '!=', 'barcode.search'),
        ]
        if model_name:
            domain.append(('model', '=', model_name))

        return IrModelFields.search(domain)

    @api.model
    def get_model_by_rule_type(self):
        """Provides a mapping for nomenclature types to Odoo models.

        The dictionary returned by this method maps barcode nomenclature rule
        types (``barcode.rule.type``) to the models that they represent.
        A barcode nomenclature rule type allows for numerical content to be
        represented in a barcode by utilizing the `......{NNDDD}`
        format to indicate the fixed and variable parts of the barcode
        respectively.

        Note: Modules adding new barcode nomenclature rule types will need
        to override this method to update the mapping in order to be supported.

        For example:
        * `weight` is defined in the Odoo `stock` module
        * `price` is defined in the Odoo `point_of_sale ` module
        * `price_to_weight ` is defined in the OCA `pos_price_to ` module

        Returns:
            dict: A mapping of models keyed by their respective barcode rule
            type (``barcode.rule.type``).
        """
        return {
            "weight": "product.product",
            "price": "product.product",
            "price_to_weight": "product.product",
        }

    @api.model
    def _search_by_barcode_barcode_fields(self, barcode, barcode_fields):
        res = []
        for barcode_field in barcode_fields:
            CurrentModel = self.env.get(barcode_field.model, False)
            if not type(CurrentModel) is bool:
                items = CurrentModel.search([
                    (barcode_field.name, "=", barcode),
                ])
                for item in items:
                    res.append({
                        "field": barcode_field,
                        "record": item,
                        "extra_data": {},
                    })
        return res
