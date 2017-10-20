"use strict";
angular.module('mobile_app_inventory').controller(
        'SelectStockLocationCtrl', [
        '$scope', '$filter', '$state', '$stateParams',
        'StockLocationModel',
        function ($scope, $filter, $state, $stateParams, StockLocationModel) {
    console.log('dans stock location ctrl')
    $scope.data = {
        'locations': [],
        'locFilter': null,
    };

    console.log('load locations')
    StockLocationModel.get_list().then(function(locations) {
        console.log('copy locations dans variable', locations);
        $scope.data.locations = locations;
    });

    $scope.$on(
        '$stateChangeSuccess',
        function(event, toState, toParams, fromState, fromParams) {
            console.log('on est dans sotck location', toParams);
            // Skip this screen if there is only one internal location
            if ($scope.data.locations.length === 1) {
                console.log('state.go direct!')
                $scope.selectLocation(
                    $scope.data.locations[0]
                );
            }
        }
    );

    $scope.selectLocation = function (location) {
        console.log('dans selectLocation')
        $state.go('product', {
            'location_id': location.id,
            'inventory_id': $stateParams.inventory_id
        });
    };

    $scope.goToLoc = function (location) {
        //if location search returns only one result, go to this location directly
        //(called on submit, so a barcode reader will trigger)
        var result = $filter('filter')($scope.data.locations, $scope.data.locFilter);
        if (result.length == 1)
            return $scope.selectLocation(result[0]);
    };

}]);
