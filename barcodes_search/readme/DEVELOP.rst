**Use in other modules**

The search will be done on all the fields named ``barcode`` in any models.

For developers, there are one handy method in ``barcode.search`` as well:

.. code-block:: python

    result = self.env['barcode.search'].search_by_barcode('12345567890123')

.. code-block:: python

    @api.model
    def search_by_barcode(self, barcode):
        """Return the record associated with the barcode.

        Args:
            barcode (str): Barcode string to search for.

        Returns: a tuple (Field, BaseModel, ExtraData)
            Field: a record of the field that matched the search
            BaseModel: A record matching the barcode, if existing
            ExtraData: An optional dictionnary that provides extra informations
        """

**Inheritance**

* If you want to make a search on a field that is not named 'barcode', you
  should overload the function ``get_barcode_fields`` of the model
  ``barcode.search``.

* If you want to implement another integration of extra data in a barcode
  via a rule, you should overload the function
  ``get_model_by_rule_type`` of the model ``barcode.search``.

For the time being, three rule types are handled:

- ``weight``, defined in Odoo ``stock`` module
- ``price``, defined in Odoo ``point_of_sale`` module
- ``price_to_weight``, defined in OCA ``pos_price_to weight`` module
