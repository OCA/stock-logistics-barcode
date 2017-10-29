"use strict";
angular.module('mobile_app_inventory').factory(
        'LocationModel', [
        '$q', 'jsonRpc',
        function ($q, jsonRpc) {

    var location_list = null;
    var locations = []

    return {
        get_list: function(force) {
            if (force){
                location_list = null;
            }
            var vals = {'inventory': false};
            location_list = location_list || jsonRpc.call(
                    'mobile.app.inventory', 'get_locations', [vals]).then(function (res) {
                return res;
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

        search_location: function(barcode) {
            var found = false;

            locations.some(function(location) {
                if (location.loc_barcode != barcode)
                    return false;
                found = location;
                return;
            });
            return found;
        },

    };
}]);
