# Copyright (C) 2014-Today GRAP (http://www.grap.coop)
# Copyright (C) 2016-Today La Louve (http://www.lalouve.net)
# Copyright 2017 LasLabs Inc.
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, exceptions, fields, models, tools

_GENERATE_TYPE = [
    ("no", "No generation"),
    ("manual", "Base set Manually"),
    ("sequence", "Base managed by Sequence"),
]


class BarcodeRule(models.Model):
    _inherit = "barcode.rule"

    # Column Section
    generate_type = fields.Selection(
        string="Generate Type",
        selection=_GENERATE_TYPE,
        required=True,
        default="no",
        help="Allow to generate barcode, including a number"
        "  (a base) in the final barcode.\n"
        " 'Base Set Manually' : User should set manually the value of the"
        " barcode base\n"
        " 'Base managed by Sequence': User will use a button to generate a"
        " new base. This base will be generated by a sequence",
    )

    generate_model = fields.Selection(
        string="Generate Model",
        selection=[],
        help="If 'Generate Type' is set, mention the model related to this" " rule.",
    )

    padding = fields.Integer(
        string="Padding", compute="_compute_padding", readonly=True, store=True
    )

    sequence_id = fields.Many2one(string="Sequence Id", comodel_name="ir.sequence")

    generate_automate = fields.Boolean(
        string="Automatic Generation",
        help="Check this to automatically generate a barcode upon creation of "
        "a new record if select rule in the model.",
    )

    general_rule = fields.Boolean(
        string="General rule",
        help="Check this to automatically generate a barcode upon creation of "
        "a new record in the mixed model.",
    )

    # Compute Section
    @api.depends("pattern")
    def _compute_padding(self):
        for rule in self:
            rule.padding = rule.pattern.count(".")

    # On Change Section
    @api.onchange("generate_type")
    def onchange_generate_type(self):
        for rule in self:
            if rule.generate_type == "no":
                rule.generate_model = False

    # Constrains Section
    @api.constrains("generate_model", "general_rule")
    def _check_generate_model_automate(self):
        """It should not allow two automated barcode generators per model.
        It also clears the cache of automated rules if necessary.
        """
        for record in self:
            if not record.general_rule:
                continue
            # This query is duplicated, but necessary because the other
            # method is cached & we need a completely current result.
            domain = [
                ("generate_model", "=", record.generate_model),
                ("general_rule", "=", True),
            ]
            if len(self.search(domain)) > 1:
                raise exceptions.ValidationError(
                    _(
                        "Only one rule per model can be used for general rule "
                        "barcode generation."
                    )
                )

    # CRUD
    @api.model
    def create(self, vals):
        self._clear_cache(vals)
        return super().create(vals)

    def write(self, vals):
        self._clear_cache(vals)
        return super().write(vals)

    # View Section
    def generate_sequence(self):
        sequence_obj = self.env["ir.sequence"]
        for rule in self:
            if rule.generate_type != "sequence":
                raise exceptions.UserError(
                    _(
                        "Generate Sequence is possible only if  'Generate Type'"
                        " is set to 'Base managed by Sequence'"
                    )
                )
            sequence = sequence_obj.create(self._prepare_sequence(rule))
            rule.sequence_id = sequence.id

    # Custom Section
    @api.model
    def _prepare_sequence(self, rule):
        return {
            "name": _("Sequence - %s") % rule.name,
            "padding": rule.padding,
        }

    @api.model
    def get_automatic_rule(self, model, rule=False):
        """It provides a cached indicator for barcode automation.

        Args:
            model (str): Name of model to search for.
        Returns:
            BarcodeRule: Recordset of automated barcode rules for model.

        """
        return self.browse(self.get_automatic_rule_ids(model, rule))

    @api.model
    @tools.ormcache("model")
    def get_automatic_rule_ids(self, model, rule=False):
        """It provides a cached indicator for barcode automation.

        Note that this cache needs to be explicitly cleared when
        `generate_automate` is changed on an associated `barcode.rule`.

        Args:
            model (str): Name of model to search for.
        Returns:
            list of int: IDs of the automated barcode rules for model.

        """
        domain = [("generate_model", "=", model), ("generate_automate", "=", True)]
        if rule:
            domain.append(("id", "=", rule.id))
        else:
            domain.append(("general_rule", "=", True))

        record = self.search(domain, limit=1)
        return record.ids

    @api.model
    def _clear_cache(self, vals):
        """It clears the caches if certain vals are updated."""
        fields = ("generate_model", "generate_automate")
        if any(k in vals for k in fields):
            self.invalidate_cache(fields)
