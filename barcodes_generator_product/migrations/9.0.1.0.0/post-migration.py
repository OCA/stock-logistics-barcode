# -*- coding: utf-8 -*-
# Copyright 2017 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


def convert_barcode_sequences(env):
    """This converts the sequences found with a barcode to barcode rules for
    being selectable at product level."""
    if not openupgrade.column_exists(
            env.cr, 'ir_sequence', 'barcode_sequence'
    ):
        # Return if product_barcode_generator was not previously installed
        return
    rule_obj = env['barcode.rule']
    env.cr.execute("""
        SELECT id, name, COALESCE(prefix, '')
        FROM ir_sequence
        WHERE barcode_sequence
        """)
    for row in env.cr.fetchall():
        rule_obj.create({
            'name': row[1],
            'type': 'product',
            'generate_model': 'product.product',
            'encoding': 'ean13',
            'pattern': row[2] + "." * (12 - len(row[2])),
            'generate_type': 'sequence',
            'sequence_id': row[0],
            'barcode_nomenclature_id': env.ref(
                'barcodes.default_barcode_nomenclature'
            ).id,
        })


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    convert_barcode_sequences(env)
