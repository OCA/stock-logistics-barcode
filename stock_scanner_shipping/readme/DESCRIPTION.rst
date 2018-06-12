[ This file must be max 2-3 paragraphs, and is required. ]

The scenario starts by calling the "Picking name input" step, then goes to a loop containing these three steps :

* Product name input
* Quantity input
* Location name input

When the user enters an empty value for the product's name, this ends the loop, and goes to the "End confirm" step.

If the user confirms, the picking is validated, otherwise, the scenario returns to the product name input step.

.. image:: images/scenario.png

