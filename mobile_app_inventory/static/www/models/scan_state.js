"use strict";
angular.module('mobile_app_inventory').factory(
    'scan_state', ['$q', function ($q) {

    var data = {};
    var callback = null;

    return {
        reset: function() {
            data.product = null;
            data.qty = null;
            return data;
        },
        set_callback: function(cb) {
            //callback for adding inventory lines
            //data will be passed in params
            //callback should return a promise
            callback = cb;
        },
        get_data: function() {
            return data;
        },
        set_inventory: function(inventory) {
            //change inventory, if inventory same as previous
            //do nothing otherwhise reset data
            //return a promise
            if (data.inventory && data.inventory.id != inventory.id) {
                //inventory changed, reset all fields
                this.reset();
                data.location = null;
            }
            data.inventory = inventory;
            return $q.when();
        },
        set_product: function(product) {
            //set product multiple time with same product
            //will increment his qty unless another product is set
            //will call callback if needed
            //return a promise
            if (!data.product) { //first set
                data.qty = 1;
                data.product = product;
            } else {
                if (data.product == product) { //unicity works even for unkwn products
                    data.qty++;
                } else {
                    //callback for the previous product and prepare for the new one
                    return this.add_inventory_line().then(function () {
                        data.product = product;
                        data.qty = 1;
                        return data;
                    });
                }
            }
            return $q.when(data);
        },
        add_inventory_line: function () {
            //few checks then call the callback
            //if callback is success, reset data
            //otherwise we want to let wrong data visible to user
            //return promise
            if (!data.product)
                return $q.when('No Product set');
            if (!data.qty)
                return $q.when("No qty set");

            return callback(data).then(this.reset);
        },
        set_qty: function(qty) {
            //call manual when user enter a number
            //return a promise
            if (!data.product) {
                return $q.reject("No product");
            }
            data.qty = qty;
            return this.add_inventory_line();
        },
        set_location: function(location) {
            //change location if needed
            //if location is different, call callback
            //return a promise
            if (data.location == location)
                //nothing to do
                return $q.when();
            if (data.product) {
                return this.add_inventory_line().then(function (ret) {
                    data.location = location;
                });
            } else {
                //product not set yet
                data.location = location;
                return $q.when();
            }
        }
    };
}]);
