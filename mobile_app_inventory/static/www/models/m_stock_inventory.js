"use strict";
angular.module('mobile_app_inventory').factory(
        'StockInventoryModel', [
        '$q', 'jsonRpc',
        function ($q, jsonRpc) {

    var inventory_list = null;

    return {
        get_list: function(force) {
            if (force){
                inventory_list = null;
            }
            inventory_list = inventory_list || jsonRpc.searchRead(
                    'stock.inventory', [['state', '=', 'confirm'], ['mobile_available', '=', true]], [
                    'id', 'name', 'date', 'inventory_line_qty',
                    ]).then(function (res) {
                return res.records;
            });
            return inventory_list;
        },

        get_inventory: function(id) {
            return this.get_list(false).then(function (inventories) {
                var found = false;
                inventories.some(function(inventory) {
                    if (inventory.id != id)
                        return false;
                    found = inventory;
                    return;
                });
                return found || $q.reject('Inventory not found');
            });
        },

        create_inventory: function(name) {
            return jsonRpc.call('stock.inventory', 'mobile_create', [name]).then(function(inventory){
                inventory_list.$$state.value.push(inventory);
                return inventory;
            });
        },

        add_inventory_line: function(inventory_id, location_id, product_id, quantity, mode) {
            return jsonRpc.call(
                    'stock.inventory', 'mobile_add_inventory_line',
                    [inventory_id, location_id, product_id, quantity, mode]).then(function (res) {
                return res;
            });
        },

    };
}]);
