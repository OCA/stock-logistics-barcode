On the form view of an inventory, once the inventory has been started
(State = *In Progress*), you will see a button **Start Barcode
Interface**. It will open a pop-up window that allows the user to easily
enter the inventory quantity (or update the inventory quantity, in case
the product is found a second time at a different place during the
inventory).

The wizard screen is automatically adapted when the product is tracked
by lot or serial, and if the inventory is made across several stock
locations.

In zero count mode, scan each article to increase its quantity by 1.
By default, each quantity change will be automatically saved as soon as another
product is identified.

In zero count and when the inventory is for a single location, the product
location will be automatically filled in according to the put-away strategy.
If the product is also located in another location and no quantity has been
inventoried, the quantity will be reset to 0 on that other location.
This allows you to put back the product on the right shelf during the
inventory.
