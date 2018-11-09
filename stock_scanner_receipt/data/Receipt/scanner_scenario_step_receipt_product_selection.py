# flake8: noqa
'Use <m> or <message> to retrieve the data transmitted by the scanner.'
'Use <t> or <terminal> to retrieve the running terminal browse record.'
'Put the returned action code in <act>, as a single character.'
'Put the returned result or message in <res>, as a list of strings.'
'Put the returned value in <val>, as an integer'

if tracer == 'loop':
    picking = env['stock.picking'].browse(terminal.reference_document)
    move = env['stock.move'].browse(int(terminal.tmp_val1))
    quantity = float(terminal.tmp_val2)
    location = env['stock.location'].search([('name', '=', message)])

    if terminal.tmp_val3:
        pack_lot_ids = [
            (0, 0, {'lot_id': int(terminal.tmp_val3), 'qty': quantity}),
        ]
    env['stock.pack.operation'].create({
        'picking_id': picking.id,
        'product_id': move.product_id.id,
        'product_uom_id': move.product_uom.id,
        'product_qty': quantity,
        'qty_done': quantity,
        'location_id': picking.location_id.id,
        'location_dest_id': location.id,
        'pack_lot_ids': pack_lot_ids,
        'linked_move_operation_ids': [(0, 0, {
            'move_id': move.id,
            'qty': quantity,
        })],
    })
elif tracer == 'picking':
    picking = env['stock.picking'].search([('name', '=', message)])
    picking.pack_operation_ids.unlink()
    terminal.reference_document = picking.id
else:
    picking = env['stock.picking'].browse(terminal.reference_document)

act = 'L'
res = [(move.id, '%g %s, %s' % (move.product_qty, move.product_uom.name, move.product_id.name)) for move in picking.move_lines if not move.linked_move_operation_ids]
if not res:
    act = 'A'
    val = ''
else:
    res += [('', _('Terminate receipt'))]
