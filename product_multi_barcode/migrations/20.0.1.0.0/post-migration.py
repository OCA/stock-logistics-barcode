# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.addons.product_multi_barcode.hooks import (
    clear_multi_variant_template_barcodes,
)


def migrate(cr, version):
    clear_multi_variant_template_barcodes(cr)
