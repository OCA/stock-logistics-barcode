# flake8: noqa
'Use <m> or <message> to retrieve the data transmitted by the scanner.'
'Use <t> or <terminal> to retrieve the running terminal browse record.'
'Put the returned action code in <act>, as a single character.'
'Put the returned result or message in <res>, as a list of strings.'
'Put the returned value in <val>, as an integer'

prodlot_name = message
move = env['stock.move'].browse(int(terminal.tmp_val1))

prodlot = env['stock.production.lot'].search([('name', '=', prodlot_name)])
if not prodlot:
    prodlot = env['stock.production.lot'].create({
        'name': prodlot_name,
        'product_id': move.product_id.id,
    })

quantity = float(terminal.tmp_val2)

terminal.tmp_val3 = prodlot.id

act = 'T'
res = [
    _('Product : %s') % move.product_id.name,
    _('Quantity : %g %s') % (quantity, move.product_uom.name),
    _('Lot : %s') % (prodlot and prodlot.name or _('None')),
    '',
    _('Location ?'),
]
