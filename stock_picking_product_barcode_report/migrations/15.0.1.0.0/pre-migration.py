# Copyright 2022 Tecnativa - Carlos Roca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade

renamed_fields = [
    (
        "res.company",
        "res_company",
        "barcode_default_format",
        "barcode_report_default_format",
    )
]


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_fields(env, renamed_fields)
