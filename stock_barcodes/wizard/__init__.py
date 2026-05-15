from . import stock_barcodes_new_lot
from . import stock_barcodes_new_packaging
from . import stock_barcodes_read
from . import stock_barcodes_read_inventory

# Loaded before stock_barcodes_read_picking because the latter declares
# candidate_picking_ids = One2many(comodel="wiz.candidate.picking", ...)
from . import stock_barcodes_candidate_picking
from . import stock_barcodes_read_picking
from . import stock_barcodes_read_todo
