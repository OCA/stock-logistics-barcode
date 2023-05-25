On start-up, the client lists available scenarii.
When the user selects a scenario, the current scenario and step are stored on the hardware configuration's entry in Odoo.

When the client sends a message to the server, the next step is selected depending on the current step and the message sent.
Then, the server returns the result of the step, which contains its type code and the text to display on the hardware screen.
Unlike the standard Odoo Workflow, each step needs to find a valid transition, because a step needs to be displayed on the hardware screen at all times.

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/154/12.0

A client for the Datalogic PowerScan scanners was developped for a very early version or this module.
The files have been removed, but are still available in the `git repository history
<https://github.com/OCA/stock-logistics-workflow/tree/527f033e9d31fe822562d4716104f37f6ce1f88c/stock_scanner/hardware/datalogic/PowerScan>`_.
