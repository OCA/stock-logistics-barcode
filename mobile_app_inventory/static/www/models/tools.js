"use strict";
angular.module('mobile_app_inventory').factory(
    'tools', ['$state', '$timeout', 'SettingModel', function ($state, $timeout, SettingModel) {

    var promise = SettingModel.get_setting('inventory_mode');

    return {
        go_to_scan_page: function(inventory_id, location_id) {
            return promise.then(function (mode) {
                var nextPage = {
                    'one_page': 'main_scan',
                    'automate': 'product'
                }[mode];
                return $state.go(nextPage, {
                    inventory_id: inventory_id,
                    location_id: location_id,
                });
            });
        },
    };
}]);
