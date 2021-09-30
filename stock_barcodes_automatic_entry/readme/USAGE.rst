To use this module, you need to:

* Define, in the view, the button that will be clicked automatically as the example below:

.. code-block:: xml

    <button name="action_automatic_entry" type="object" string="Automatic entry" icon="fa-plus"
            class="btn-primary barcode-automatic-entry" invisible="1"
    />

* Define the logic to be executed upon button clicking

.. code-block:: python

    def action_automatic_entry(self):
        # Execute specific logic
        return
