# flake8: noqa
# Use <m> or <message> to retrieve the data transmitted by the scanner.
# Use <t> or <terminal> to retrieve the running terminal browse record.
# Put the returned action code in <act>, as a single character.
# Put the returned result or message in <res>, as a list of strings.
# Put the returned value in <val>, as an integer


location = model.search([('name', '=', message.get('location_name'))])

data = []

location_infos = env['stock.quant'].read_group(
    [('location_id.name', '=', message.get('location_name')),
     ('location_id.usage', '=', 'internal')],
    ['location_id', 'lot_id', 'qty', 'product_id', 'product_id.uom_id'],
    ['product_id'],
)
for location_info in location_infos:
    product = env['product.product'].browse(location_info['product_id'][0])
    data.append({
        'product': location_info['product_id'][1],
        'product_uom': product.uom_id.name,
        'product_qty': location_info['qty']
    })

act = 'W'
val = {
    'items': data,
    'location_name': location.name
}
res = 'stock_scanner_web_location_info.location_show'
