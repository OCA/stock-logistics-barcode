# © 2015 Roberto Lizana (Trey)
# © 2016 Pedro M. Baeza
# © 2018 Xavier Jimenez (QubiQ)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


def post_init_hook(cr, registry):
    cr.execute(
        """
    INSERT INTO product_barcode
    (product_id, product_tmpl_id, name, sequence)
    SELECT id, product_tmpl_id, barcode, 0
    FROM product_product
    WHERE barcode IS NOT NULL"""
    )
