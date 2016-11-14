angular.module('scan_to_inventory').controller(
        'SelectStockLocationCtrl', [
        '$scope', '$rootScope', 'jsonRpc', '$state', 'StockInventoryModel',
        function ($scope, $rootScope, jsonRpc, $state, StockInventoryModel) {

    $scope.data = {
        'location_qty': 0,
        'location_list': false,
    };

    $scope.$on(
            '$stateChangeSuccess',
            function(event, toState, toParams, fromState, fromParams){
        if ($state.current.name === 'select_stock_location') {
            $scope.data.location_list = $rootScope.LocationList;
            $scope.data.location_qty = $rootScope.LocationList.length;
            // Skip this screen if there is only one internal location
            if ($rootScope.LocationList.length === 1){
            $rootScope.currentLocationId = $rootScope.LocationList[0].id;
            $rootScope.currentLocationName = $rootScope.LocationList[0].name;
            $state.go('select_product_product');
            }
        }
    });

    $scope.selectLocation = function (location_id, location_name) {
        $rootScope.currentLocationId = location_id;
        $rootScope.currentLocationName = location_name;
        $state.go('select_product_product');
    };

}]);
