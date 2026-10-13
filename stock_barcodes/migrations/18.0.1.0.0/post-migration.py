from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    old_show_pending_moves = openupgrade.get_legacy_name("show_pending_moves")
    openupgrade.logged_query(
        env.cr,
        f"""
        UPDATE stock_barcodes_option_group
        SET show_pending_moves = CASE
            WHEN {old_show_pending_moves} IS TRUE  THEN 'pending'
            WHEN {old_show_pending_moves} IS FALSE THEN 'all'
            ELSE show_pending_moves  -- keep value if NULL just in case
        END
        WHERE {old_show_pending_moves} IS NOT NULL;
        """,
    )
