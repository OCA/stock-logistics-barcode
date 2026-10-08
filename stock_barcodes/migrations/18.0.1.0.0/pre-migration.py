from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE stock_move_line
            ADD COLUMN IF NOT EXISTS qty_picked numeric;
        UPDATE stock_move_line set qty_picked = qty_done;
        """,
    )
    openupgrade.rename_columns(
        env.cr,
        {"stock_barcodes_option_group": [("show_pending_moves", None)]},
    )
