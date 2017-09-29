"use strict";
angular.module('mobile_app_inventory').controller(
        'SelectStockLocationCtrl', [
        '$scope', '$rootScope', '$state',
        'StockInventoryModel', 'StockLocationModel',
        function ($scope, $rootScope, $state, StockInventoryModel, StockLocationModel) {

    $scope.data = {
        'location_list': false,
    };

    console.log('load locations')
    StockLocationModel.get_list().then(function(locations) {
        console.log('copy locations dans variable', locations);
        $scope.data.locations = locations;
    });

    $scope.$on(
            '$stateChangeSuccess',
            function(event, toState, toParams, fromState, fromParams) {
        if ($state.current.name === 'select_stock_location') {
            // Skip this screen if there is only one internal location
            if ($scope.data.locations.length === 1) {
                $scope.selectLocation(
                    $scope.data.locations[0].id,
                    $scope.data.locations[0].name
                );
            }
        }
    });

    $scope.selectLocation = function (location_id, location_name) {
        $rootScope.currentLocationId = location_id;
        $rootScope.currentLocationName = location_name;
        $state.go('select_product_product');
    };

}]);
