"use strict";
angular.module('mobile_app_inventory').factory(
        'LocationModel', [
        '$q', 'jsonRpc',
        function ($q, jsonRpc) {

    function reset() {
        data.locations = [];
        data.location_promise = null;
    }
    var data = {}
    reset();

    return {
        get_list: function(inventory) {
            //get locations for a given inventory
            //retrun a promise
            if (inventory)
                reset();

            data.location_promise = data.location_promise || jsonRpc.call(
                'mobile.app.inventory', 'get_locations', [{'inventory': inventory}]
                ).then(function (res) {
                    data.locations = res;
                    return res;
                }
            );
            return data.location_promise;
        },

        get_location: function(id) {
            //search from an location id
            //return a promise
            return this.get_list().then(function (locations) {
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

        search_location: function(barcode) {
            //search from a barcode
            //search in cache, no promise
            var found = false;
            data.locations.some(function(location) {
                if (location.barcode != barcode)
                    return false;
                found = location;
                return;
            });
            return found;
        },

    };
}]);
