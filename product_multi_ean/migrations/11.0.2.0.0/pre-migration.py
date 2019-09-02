# Copyright 2019 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade

models_to_rename = [
    ('product.ean13', 'product.barcode')
]


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_tables(
        env.cr, [
            ('product_ean13', 'product_barcode'),
        ],
    )
    openupgrade.rename_models(env.cr, models_to_rename)
