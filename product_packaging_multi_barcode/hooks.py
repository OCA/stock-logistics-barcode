# Copyright 2023 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


def post_init_hook(cr, registry):
    cr.execute(
        """
    INSERT INTO product_barcode
    (packaging_id, name, sequence)
    SELECT id, barcode, 0
    FROM product_packaging
    WHERE barcode IS NOT NULL"""
    )
