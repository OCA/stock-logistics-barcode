"use strict";
angular.module('mobile_app_inventory').factory(
        'StockLocationModel', [
        '$q', '$rootScope', 'jsonRpc',
        function ($q, $rootScope, jsonRpc) {

    var location_list = null;

    return {
        get_list: function(force=false) {
            if (force){
                location_list = null;
            }
            location_list = location_list || jsonRpc.searchRead(
                    'stock.location', [['usage', '=', 'internal'], ['mobile_available', '=', true]], [
                    'id', 'name', 'parent_complete_name',
                    ]).then(function (res) {
                //$rootScope.LocationList = res.records;
                //return res.records.length;
                return res.records;
            });
            return location_list;
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
        },

    };
}]);
