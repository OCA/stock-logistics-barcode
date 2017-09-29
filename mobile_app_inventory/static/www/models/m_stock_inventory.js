"use strict";
angular.module('mobile_app_inventory').factory(
        'StockInventoryModel', [
        '$q', '$rootScope', 'jsonRpc',
        function ($q, $rootScope, jsonRpc) {

    var inventory_list = null;

    return {
        get_list: function() {
            console.log('on charge draft inventory list');
            inventory_list = inventory_list || jsonRpc.searchRead(
                    'stock.inventory', [['state', '=', 'confirm']/*, ['scan_ok', '=', false]*/], [
                    'id', 'name', 'date', 'inventory_line_qty',
                    ]).then(function (res) {
                return res.records;
            });
            return inventory_list;
        },
        CreateInventory: function(name) {
            return jsonRpc.call('stock.inventory', 'create_by_scan', [name])
        },
        LoadInventory: function(orderId) {
            return jsonRpc.searchRead(
                    'stock.inventory', [['id', '=', orderId]], [
                    'id', 'name', 'date', 'inventory_line_qty']).then(function (res) {
                return res.records[0];
            });
        },
        AddInventoryLine: function(inventoryId, locationId, productId, quantity, mode) {
            return jsonRpc.call(
                    'stock.inventory', 'add_inventory_line_by_scan',
                    [inventoryId, locationId, productId, quantity, mode]).then(function (res) {
                return res;
            });
        },
        get_inventory: function(id) {
            return this.get_list().then(function (invs) {
                var found = false;
                invs.some(function(i)  {
                    if (i.id != id)
                        return false;
                    found = i;
                    return;
                });
                console.log('found :' , found)
                return found || $q.reject('Inventory not found');
            });
        }
    };
}]);
