This module installs a scenario which allows the user to process an incoming picking.

The scenario starts by calling the "Picking name input" step, then goes to a loop containing these four steps :

* Product name input
* Quantity input
* Lot name input (if applicable)
* Location name input

When the user enters an empty value for the product's name, this ends the loop, and goes to the "End confirm" step.

If the user confirms, the picking is validated, otherwise, the scenario returns to the product name input step.

.. image:: images/scenario.png