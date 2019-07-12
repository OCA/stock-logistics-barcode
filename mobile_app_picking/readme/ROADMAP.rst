* For the time being, this module doesn't handle 'Lot', 'Pack' and 'Owner'.

* The UI doesn't allow to add an unexpected product on the fly.

* In practice, the mobile app emulate the actions of the user, changing
  Done quantity of stock moves of a given picking.
  This action is allowed by odoo under certain conditions, that are
  defined by the field ``is_quantity_done_editable`` of the ``stock.picking``.
  Using this module if this field is unchecked could generate problems.
  This field is disabled (amoung others conditions) if user is member of
  ``stock.group_stock_multi_locations`` or ``stock.group_tracking_owner``
  See the functions ``_compute_show_details_visible`` and
  ``_compute_is_quantity_done_editable`` for more detals.
  
