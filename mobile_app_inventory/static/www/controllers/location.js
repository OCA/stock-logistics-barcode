"use strict";
angular.module('mobile_app_inventory').controller(
    'LocationCtrl', [
    '$scope', '$filter', '$state', '$stateParams','LocationModel',
    function ($scope, $filter, $state, $stateParams, LocationModel) {
    $scope.data = {
        'location_list': [],
        'location_filter': null,
    };

    $scope.$on(
        '$stateChangeSuccess',
        function(event, toState, toParams, fromState, fromParams) {
        if ($state.current.name === 'location') {

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
        $state.go('product', {
            'inventory_id': $stateParams.inventory_id,
            'location_id': location.id,
        });
    };

    $scope.search_location = function () {
        //if location search returns only one result, go to this location directly
        //(called on submit, so a barcode reader will trigger)
        var result = $filter('filter')($scope.data.location_list, $scope.data.location_filter);
        if (result.length == 1)
            return $scope.select_location(result[0]);
    };

}]);
