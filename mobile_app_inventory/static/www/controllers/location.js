"use strict";
angular.module('mobile_app_inventory').controller(
    'LocationCtrl', [
        '$scope',
        '$filter',
        '$state',
        '$stateParams',
        'LocationModel',
        'InventoryModel',
        'ProductModel',
        'scan_state',
        function (
            $scope,
            $filter,
            $state,
            $stateParams,
            LocationModel,
            InventoryModel,
            ProductModel,
            scan_state,
        ) {
    $scope.data = {
        'location_list': [],
        'location_filter': null,
    };

    $scope.$on(
        '$stateChangeSuccess',
        function(event, toState, toParams, fromState, fromParams) {
            if (['location', 'select_location'].indexOf(
                $state.current.name
            ) !== -1) {
            $scope.data.location_filter = null;
            LocationModel.get_list({id: $stateParams.inventory_id}).then(function(location_list) {
                $scope.data.location_list = location_list;
                // Skip this screen if there is only one internal location
                if ($scope.data.location_list.length === 1) {
                    $scope.select_location($scope.data.location_list[0]);
                }
            });
        }
    });

    $scope.select_location = function (location) {
        var inventory_name = $stateParams.inventory_name;
        var inventory_id = $stateParams.inventory_id;
        if (!inventory_id && inventory_name) {
            InventoryModel.create_inventory(
                inventory_name,
                location.id,
            ).then(
                function(inventory){
                    scan_state.set_inventory(inventory);
                    // FIXME: it calls inventory function to call back this function with an inventory_id. There should be a cleaner way.
                    $scope.select_inventory(inventory.id);
                }
            );
        } else {
            $state.go('product', {
                'inventory_id': $stateParams.inventory_id,
                'location_id': location.id
            });
        }
    };

    $scope.search_location = function () {
        //if location search returns only one result, go to this location directly
        //(called on submit, so a barcode reader will trigger)
        var result = $filter('filter')($scope.data.location_list, $scope.data.location_filter);
        if (result.length == 1)
            return $scope.select_location(result[0]);
    };

    $scope.select_inventory = function (inventory_id) {
        ProductModel.get_list({id:inventory_id}).then(function(product_list) {
            $state.go('location', {inventory_id: inventory_id});
        });
    };
}]);
