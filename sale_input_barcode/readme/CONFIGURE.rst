Optionnaly you may prevent to create unknown lot if you add this code in your custom code.


.. code-block:: python

    class SaleOrderLine(models.Model):
        _inherit = "sale.order.line"

        def _create_unknown_lot(self, barcode):
            return False
