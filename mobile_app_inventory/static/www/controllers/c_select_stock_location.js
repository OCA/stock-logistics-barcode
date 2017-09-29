"use strict";
angular.module('mobile_app_inventory').controller(
        'SelectStockLocationCtrl', [
        '$scope', '$rootScope', '$state', '$stateParams',
        'StockLocationModel',
        function ($scope, $rootScope, $state, $stateParams, StockLocationModel) {
    console.log('dans stock location ctrl')
    $scope.data = {
        'locations': [],
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

}]);
