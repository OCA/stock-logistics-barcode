# Copyright 2021 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import tools


def pre_init_hook(cr):
    if not tools.column_exists(cr, "stock_move_line", "barcode_scan_state"):
        cr.execute(
            """
            ALTER TABLE stock_move_line
            ADD COLUMN barcode_scan_state varchar"""
        )
        cr.execute(
            """
            UPDATE stock_move_line sml
            SET barcode_scan_state = 'pending'
            """
        )
