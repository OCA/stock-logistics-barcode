# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    # accumulate_read_quantity was only read by the inventory screen, which always
    # uses this group, to add a reading to the counted quantity instead of
    # replacing it. That choice is now no_increase_qty_done (unset adds), and
    # accumulate_read_quantity accumulates repeated readings on the screen before
    # a manual confirmation, so keep the inventory behavior and leave the new one
    # disabled.
    inventory_group = env.ref(
        "stock_barcodes.stock_barcodes_option_group_inventory",
        raise_if_not_found=False,
    )
    if inventory_group:
        openupgrade.logged_query(
            env.cr,
            """
            UPDATE stock_barcodes_option_group
            SET no_increase_qty_done = NOT COALESCE(accumulate_read_quantity, FALSE)
            WHERE id = %s
            """,
            (inventory_group.id,),
        )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE stock_barcodes_option_group
        SET accumulate_read_quantity = FALSE
        WHERE accumulate_read_quantity
        """,
    )
    # 15.0 value of the stock moves source, never mapped when the picking field
    # was renamed to move_ids
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE stock_barcodes_option_group
        SET source_pending_moves = 'move_ids'
        WHERE source_pending_moves = 'move_lines'
        """,
    )
