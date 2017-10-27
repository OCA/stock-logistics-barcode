"use strict";
angular.module('mobile_app_inventory').factory(
        'StockLocationModel', [
        '$q', 'jsonRpc',
        function ($q, jsonRpc) {

    var location_list = null;

    return {
        get_list: function(force) {
            if (force){
                location_list = null;
            }
            location_list = location_list || jsonRpc.searchRead(
                    'stock.location', [['usage', '=', 'internal'], ['mobile_available', '=', true]], [
                    'id', 'name', 'parent_complete_name',
                    ]).then(function (res) {
                return res.records;
            });
            return location_list;
        },

        get_location: function(id) {
            return this.get_list(false).then(function (locations) {
                var found = false;
                locations.some(function(location) {
                    if (location.id != id)
                        return false;
                    found = location;
                    return;
                });
                return found || $q.reject('Location not found');
            });
        },

    };
}]);
