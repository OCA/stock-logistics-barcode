# flake8: noqa
'Use <m> or <message> to retrieve the data transmitted by the scanner.'
'Use <t> or <terminal> to retrieve the running terminal browse record.'
'Put the returned action code in <act>, as a single character.'
'Put the returned result or message in <res>, as a list of strings.'
'Put the returned value in <val>, as an integer'

terminal.tmp_val2 = message

move = env['stock.move'].browse(int(terminal.tmp_val1))
quantity = float(terminal.tmp_val2)

act = 'T'
res = [
    _('Product : %s') % move.product_id.name,
    _('Quantity : %g %s') % (quantity, move.product_uom.name),
    '',
    _('Location ?'),
]
