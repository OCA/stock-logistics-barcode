Optionnaly you may prevent to create unknown lot if you add this code in your custom code.


.. code-block:: python

    class PurchaseOrderLine(models.Model):
        _inherit = "purchase.order.line"

        def _create_unknown_lot(self, barcode):
            return False
