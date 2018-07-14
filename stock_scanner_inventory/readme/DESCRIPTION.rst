This module installs a scenario which allows the user to create and validate an inventory.

The scenario starts by a loop containing these three steps :

* Product name input
* Quantity input
* Location name input

When the user enters an empty value for the product's name, this ends the loop, and goes to the "End confirm" step.

If the user confirms, the inventory is validated, otherwise, the scenario returns to the product name input step.

.. image:: images/scenario.png
