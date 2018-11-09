# flake8: noqa
'Use <m> or <message> to retrieve the data transmitted by the scanner.'
'Use <t> or <terminal> to retrieve the running terminal browse record.'
'Put the returned action code in <act>, as a single character.'
'Put the returned result or message in <res>, as a list of strings.'
'Put the returned value in <val>, as an integer'

if tracer == 'loop':
    picking = env['stock.picking'].browse(terminal.reference_document)
    move = env['stock.move'].browse(int(terminal.get_tmp_value('tmp_val1')))
    quantity = float(terminal.get_tmp_value('tmp_val2'))
    location = env['stock.location'].search([('name', '=', message)])

    s_m_l = {
        'picking_id': picking.id,
        'product_id': move.product_id.id,
        'move_id': move.id,
        'product_uom_id' :  move.product_uom.id,
        'location_id': picking.location_id.id,
        'location_dest_id': location.id,
        'qty_done': quantity,
    }

    if terminal.get_tmp_value('tmp_val3'):
        s_m_l['lot_id'] =  int(terminal.get_tmp_value('tmp_val3'))



    env['stock.move.line'].create(s_m_l)


elif tracer == 'picking':
    picking = env['stock.picking'].search([('name', '=', message)])
    picking.move_lines.move_line_ids.unlink()
    terminal.reference_document = picking.id
else:
    picking = env['stock.picking'].browse(terminal.reference_document)

act = 'L'
res = [(move.id, '%g %s, %s' % (move.product_uom_qty - move.quantity_done, move.product_uom.name, move.product_id.name)) for move in picking.move_lines ]

if not res:
    act = 'A'
    val = ''
else:
    res += [('', _('Terminate receipt'))]
