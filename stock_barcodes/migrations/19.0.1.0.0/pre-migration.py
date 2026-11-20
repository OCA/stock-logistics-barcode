# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    # Packagings are units of measure in 19.0: the scan screen field is now
    # packaging_uom_id. The options data is noupdate and users can create their
    # own options, so rename the field in every existing option.
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE stock_barcodes_option
        SET field_name = 'packaging_uom_id'
        WHERE field_name = 'packaging_id'
        """,
    )
