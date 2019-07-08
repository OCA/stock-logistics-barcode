# flake8: noqa
'Use <m> or <message> to retrieve the data transmitted by the scanner.'
'Use <t> or <terminal> to retrieve the running terminal browse record.'
'Put the returned action code in <act>, as a single character.'
'Put the returned result or message in <res>, as a list of strings.'
'Put the returned value in <val>, as an integer'

move = env['stock.move'].browse(int(terminal.get_tmp_value('tmp_val1')))

quantity = float(message)
terminal.set_tmp_value('tmp_val2', quantity)

prodlot = env['stock.move'].browse(int(terminal.get_tmp_value('tmp_val3')))

act = 'T'
res = [
    _('Product : %s') % move.product_id.name,
    _('Quantity : %g %s') % (quantity, move.product_uom.name),
    _('Lot : %s') % (prodlot and prodlot.name or _('None')),
    '',
    _('Location ?'),
]
