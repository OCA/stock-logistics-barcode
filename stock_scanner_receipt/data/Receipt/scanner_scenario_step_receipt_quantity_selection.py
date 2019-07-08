# flake8: noqa
'Use <m> or <message> to retrieve the data transmitted by the scanner.'
'Use <t> or <terminal> to retrieve the running terminal browse record.'
'Put the returned action code in <act>, as a single character.'
'Put the returned result or message in <res>, as a list of strings.'
'Put the returned value in <val>, as an integer'

move = env['stock.move'].browse(int(terminal.get_tmp_value('tmp_val1')))

prodlot_name = message
prodlot = env['stock.production.lot'].search([('name', '=', prodlot_name)])
if not prodlot:
    prodlot = env['stock.production.lot'].create({
        'name': prodlot_name,
        'product_id': move.product_id.id,
    })


terminal.set_tmp_value('tmp_val3', prodlot.id)

act = 'Q'
res = [
    _('Product : %s' % move.product_id.name),
]
product_tracking = move.product_id.tracking
if product_tracking != 'none':
    res.append(
        _('Lot : %s') % (prodlot and prodlot.name or _('None')),
    )
res += [
    '',
    _('Quantity ?'),
]
val = max(move.product_uom_qty - move.quantity_done, 0.0)
