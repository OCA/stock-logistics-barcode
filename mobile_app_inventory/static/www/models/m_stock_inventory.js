"use strict";
angular.module('mobile_app_inventory').factory(
        'StockInventoryModel', [
        '$q', '$rootScope', 'jsonRpc',
        function ($q, $rootScope, jsonRpc) {

    return {
        LoadDraftInventoryList: function() {
            console.log('on charge draft inventory list');
            return jsonRpc.searchRead(
                    'stock.inventory', [['state', '=', 'confirm']/*, ['scan_ok', '=', false]*/], [
                    'id', 'name', 'date', 'inventory_line_qty',
                    ]).then(function (res) {
                $rootScope.DraftInventoryList = res.records;
                return res.records.length;
            });
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

    };
}]);
