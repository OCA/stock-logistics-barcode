# Copyright 2023 ForgeFlow <http://www.forgeflow.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


def delete_fk_constraints(env):
    # delete obsolete model references
    openupgrade.remove_tables_fks(env.cr, ["wiz_stock_barcodes_read_inventory"])


@openupgrade.migrate()
def migrate(env, version):
    delete_fk_constraints(env)
