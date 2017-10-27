"use strict";

var fsm = (function state() {
	var data = {};
	var service = null;

	return {
		set_service: function(srv) {
			service = srv;
		},
		get_data: function() {
			//pour les views
			return data;
		},
		set_inventory: function(inventory) {
			//TODO: faire un reset lorsqu'on change d'inventory
			data.inventory = inventory;
		},
		set_product: function(product) {
			console.log('set product', product, data);
			if (!data.product) {
				data.qty = 1;
				data.product = product;
			} else {
				if (data.product == product) { // todo unicity ?
					data.qty++;
				} else {
					return this.add_inventory_line().then(function () {
						data.product = product;
						data.qty = 1;
						return data;
					});
				}
			}
			return Promise.resolve(data);
		},
		add_inventory_line: function () {
			console.log('add_inventory_line', data);
			//todo renvoyer des Promise.reject
			if (!data.product)
				throw "no product";
			if (!data.qty)
				throw "no qty";
			return Promise.resolve("ici le vrai call"); //remove me
			return srv.add_inventory_line(
				data.inventory.id,
				data.location.id,
				data.product.id, 
				data.qty, 
				'ask'
			);

		},
		set_qty: function(qty) {
			console.log('set qty', qty);
			if (!data.product) {
				throw "no product";
			}
			data.qty = qty;
			return Promise.resolve();
		},
		set_location: function(location) {
			console.log('set location', location);
			if (data.location == location)
				//nothing to do
				return Promise.resolve();
			if (data.product) {
				return this.add_inventory_line().then(function () {
					data.location = location;
					data.product = null;
					data.qty = null;
				});
			} else {
				data.location = location;
				return Promise.resolve();
			}
		}
	};
})()
