"use strict";
angular.module('mobile_app_inventory').factory(
        'InventoryModel', [
        '$q', 'jsonRpc',
        function ($q, jsonRpc) {

    return {
        get_list: function() {
            //always a fresh list
            return jsonRpc.call(
                    'mobile.app.inventory', 'get_inventories', []).then(function (res) {
                return res;
            });
        },

        get_inventory: function(id) {
            return this.get_list().then(function (inventories) {
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
                return inventory;
            });
        },

        add_inventory_line: function(inventory, location, product, quantity, mode) {
            var vals = {
                'inventory': {'id': inventory.id},
                'location': {'id': location.id},
                'product': {'id': product.id, 'barcode': product.barcode},
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
