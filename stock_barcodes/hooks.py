# Copyright 2021 Tecnativa - Sergio Teruel
# Copyright 2024 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


def pre_init_hook(cr):
    openupgrade.logged_query(
        cr,
        """
        ALTER TABLE stock_move_line
            ADD COLUMN IF NOT EXISTS barcode_scan_state VARCHAR DEFAULT 'pending';
        ALTER TABLE stock_move_line ALTER COLUMN barcode_scan_state DROP DEFAULT;
        """,
    )
    openupgrade.logged_query(
        cr,
        """
        ALTER TABLE stock_move
            ADD COLUMN IF NOT EXISTS barcode_backorder_action VARCHAR DEFAULT 'pending';
        ALTER TABLE stock_move ALTER COLUMN barcode_backorder_action DROP DEFAULT;
        """,
    )
