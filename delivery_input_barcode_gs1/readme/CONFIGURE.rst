Optionnaly you may prevent to create unknown lot if you add this code in your custom code.


.. code-block:: python

    class StockMoveLine(models.Model):
        _inherit = "stock.move.line"

        def _create_unknown_lot(self, barcode):
            return False
