# © 2015 Roberto Lizana (Trey)
# © 2016 Pedro M. Baeza
# © 2018 Xavier Jimenez (QubiQ)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


def post_init_hook(env):
    env.cr.execute(
        """
    INSERT INTO product_barcode
    (product_id, product_tmpl_id, name, sequence)
    SELECT id, product_tmpl_id, barcode, 0
    FROM product_product
    WHERE barcode IS NOT NULL"""
    )
    clear_multi_variant_template_barcodes(env.cr)


def clear_multi_variant_template_barcodes(cr):
    """Barcodes live on the variants: a template with several active variants
    keeps no barcode of its own."""
    cr.execute(
        """
    UPDATE product_template pt
    SET barcode = NULL
    WHERE pt.barcode IS NOT NULL
    AND (
        SELECT count(*)
        FROM product_product pp
        WHERE pp.product_tmpl_id = pt.id AND pp.active
    ) > 1"""
    )
