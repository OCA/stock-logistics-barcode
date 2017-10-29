"use strict";
angular.module('mobile_app_inventory').factory(
        'InventoryModel', [
        '$q', 'jsonRpc',
        function ($q, jsonRpc) {

    var inventory_list = null;

    return {
        get_list: function(force) {
            if (force){
                inventory_list = null;
            }
            inventory_list = inventory_list || jsonRpc.call(
                    'mobile.app.inventory', 'get_inventories', []).then(function (res) {
                return res;
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
            var vals = {'inventory': {'name': name}}
            return jsonRpc.call('mobile.app.inventory', 'create_inventory', [vals]).then(function(inventory){
                inventory_list.$$state.value.push(inventory);
                return inventory;
            });
        },

        add_inventory_line: function(inventory_id, location_id, product_id, quantity, mode) {
            var vals = {
                'inventory': {'id': inventory_id},
                'location': {'id': location_id},
                'product': {'id': product_id},
                'qty': quantity,
                'mode': mode,
            }
            return jsonRpc.call(
                    'mobile.app.inventory', 'add_inventory_line', [vals]).then(function (res) {
                return res;
            });
        },

    };
}]);
