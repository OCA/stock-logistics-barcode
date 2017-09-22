"use strict";
angular.module('mobile_app_inventory').factory(
    'tools', ['$state', '$timeout', 'SettingModel', function ($state, $timeout, SettingModel) {

    return {
        go_to_scan_page: function(inventory_id, location_id) {
            SettingModel.get_setting('inventory_mode').then(function (setting) {
                $timeout(function() {
                    if (setting === 'one_page'){
                        $state.go('main_scan', {
                            inventory_id: inventory_id,
                            location_id: location_id,
                        });
                    } else if (setting === 'automate') {
                        $state.go('product', {
                            inventory_id: inventory_id,
                            location_id: location_id,
                        });
                    }
                }, 10);
            });
        },
    };
}]);
