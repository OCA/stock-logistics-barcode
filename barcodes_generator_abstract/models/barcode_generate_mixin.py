# Copyright (C) 2014-TODAY GRAP (http://www.grap.coop)
# Copyright (C) 2016-TODAY La Louve (http://www.lalouve.net)
# Copyright 2017 LasLabs Inc.
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import re

import barcode

from odoo import _, api, exceptions, fields, models


class BarcodeGenerateMixin(models.AbstractModel):
    _name = "barcode.generate.mixin"
    _description = "Generate Barcode Mixin"

    # Column Section
    barcode_rule_id = fields.Many2one(
        string="Barcode Rule",
        comodel_name="barcode.rule",
        help="Select a rule to generate a barcode",
    )

    barcode_base = fields.Integer(
        copy=False,
        help="This value is used to generate barcode"
        " according to the setting of the barcode rule.",
    )

    generate_type = fields.Selection(
        related="barcode_rule_id.generate_type",
    )

    @api.model_create_multi
    def create(self, vals_list):
        """It creates a new barcode if automation is active."""
        records = super().create(vals_list)
        for rec in records:
            rule = rec.barcode_rule_id
            if rule and rule.generate_automate and rule.generate_type == "sequence":
                if not rec.barcode_base:
                    rec.generate_base()
                if not rec.barcode:
                    rec.generate_barcode()
        return records

    def write(self, vals):
        """Generate new barcodes if a barcode rule with automation
        is applied."""
        res = super().write(vals)
        if vals.get("barcode_rule_id"):
            rule = self.env["barcode.rule"].browse(vals["barcode_rule_id"])
            if rule.generate_automate and rule.generate_type == "sequence":
                for rec in self:
                    if not rec.barcode_base:
                        rec.generate_base()
                    if not rec.barcode:
                        rec.generate_barcode()
        return res

    # View Section
    def generate_base(self):
        for item in self:
            if item.generate_type != "sequence":
                raise exceptions.UserError(
                    _(
                        "Generate Base can be used only with barcode rule with"
                        " 'Generate Type' set to 'Base managed by Sequence'"
                    )
                )
            else:
                item.barcode_base = item.barcode_rule_id.sequence_id.next_by_id()

    def generate_barcode(self):
        for item in self:
            padding = item.barcode_rule_id.padding
            str_base = str(item.barcode_base).rjust(padding, "0")
            custom_code = self._get_custom_barcode(item)
            if custom_code:
                custom_code = custom_code.replace("." * padding, str_base)
                barcode_class = barcode.get_barcode_class(item.barcode_rule_id.encoding)
                item.barcode = barcode_class(custom_code).get_fullcode()

    # Custom Section
    @api.model
    def _get_custom_barcode(self, item):
        """
        If the pattern is '23.....{NNNDD}'
        this function will return '23.....00000'
        Only replace N and D inside braces, and remove the braces in the result.
        Note : Overload _get_replacement_char to have another char
        instead that replace 'N' and 'D' char.
        """
        if not item.barcode_rule_id:
            return False

        pattern = item.barcode_rule_id.pattern

        def _replace_inside_braces(match):
            content = match.group(1)
            content = content.replace("N", self._get_replacement_char("N"))
            content = content.replace("D", self._get_replacement_char("D"))
            return content

        custom_code = re.sub(r"\{([^}]*)\}", _replace_inside_braces, pattern)
        return custom_code

    @api.model
    def _get_replacement_char(self, char):
        """
        Can be overload by inheritance
        Define wich character will be used instead of the 'N' or the 'D'
        char, present in the pattern of the barcode_rule_id
        """
        return "0"
