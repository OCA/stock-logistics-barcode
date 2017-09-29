"use strict";
angular.module('mobile_app_inventory').factory(
        'StockLocationModel', [
        '$q', '$rootScope', 'jsonRpc',
        function ($q, $rootScope, jsonRpc) {

    var locations = null;
    return {
        get_list: function() {
            locations = locations || jsonRpc.searchRead(
                    'stock.location', [['usage', '=', 'internal']], [
                    'id', 'name', 'parent_complete_name',
                    ]).then(function (res) {
                //$rootScope.LocationList = res.records;
                //return res.records.length;
                return res.records;
            });
            return locations;
        },
        get_location: function(id) {
            return this.get_list().then(function (locs) {
                var found = false;
                locs.some(function(l)  {
                    if (l.id != id)
                        return false;
                    found = l;
                    return;
                });
                return found || $q.reject('Location not found');
            });
        }
    };
}]);
