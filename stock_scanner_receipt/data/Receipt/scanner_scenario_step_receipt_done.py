# flake8: noqa
'Use <m> or <message> to retrieve the data transmitted by the scanner.'
'Use <t> or <terminal> to retrieve the running terminal browse record.'
'Put the returned action code in <act>, as a single character.'
'Put the returned result or message in <res>, as a list of strings.'
'Put the returned value in <val>, as an integer'

picking = model.browse(terminal.reference_document)
picking.do_transfer()

act = 'F'
res = [
    _('Receipt done.'),
]

backorder = model.search([('backorder_id', '=', picking.id)])
if backorder:
    res += [
        '',
        _('A backorder was created : %s') % backorder.name,
    ]
