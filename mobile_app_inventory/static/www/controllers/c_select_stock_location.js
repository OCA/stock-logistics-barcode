"use strict";
angular.module('mobile_app_inventory').controller(
        'SelectStockLocationCtrl', [
        '$scope', '$filter', '$state', '$stateParams',
        'StockLocationModel',
        function ($scope, $filter, $state, $stateParams, StockLocationModel) {
    $scope.data = {
        'location_list': [],
        'location_filter': null,
    };

    $scope.$on(
            '$stateChangeSuccess',
            function(event, toState, toParams, fromState, fromParams) {
        if ($state.current.name === 'location') {
            StockLocationModel.get_list(false).then(function(location_list) {
                $scope.data.location_list = location_list;
                // Skip this screen if there is only one internal location
                if ($scope.data.location_list.length === 1) {
                    $scope.select_location($scope.data.location_list[0]);
                }
            });
        }
    });

    $scope.select_location = function (location) {
        $state.go('product', {
            'location_id': location.id,
            'inventory_id': $stateParams.inventory_id,
        });
    };

    $scope.search_location = function (location) {
        //if location search returns only one result, go to this location directly
        //(called on submit, so a barcode reader will trigger)
        var result = $filter('filter')($scope.data.location_list, $scope.data.location_filter);
        if (result.length == 1)
            return $scope.select_location(result[0]);
    };

}]);
