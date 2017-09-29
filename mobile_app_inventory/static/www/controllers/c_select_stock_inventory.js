"use strict";
angular.module('mobile_app_inventory').controller(
        'SelectStockInventoryCtrl', [
        '$scope', '$rootScope', '$state', 'StockInventoryModel', '$translate',
        function ($scope, $rootScope, $state, StockInventoryModel, $translate) {

    $scope.data = {
        'inventories': [],
    };
    console.log('on init DraftInventoryList')
    StockInventoryModel.get_list().then(function (inventories) {
        $scope.data.inventories = inventories;
    });

    $scope.$on(
            '$stateChangeSuccess',
            function(event, toState, toParams, fromState, fromParams){
        if ($state.current.name === 'select_stock_inventory') {
            $scope.data.inventory_name = '';
        }
    });

    $scope.selectInventory = function (id) {
        $rootScope.currentInventoryId = id;
        $state.go('select_stock_location');
    };

    $scope.submit = function () {
        if ($scope.data.inventory_name !== '') {
            StockInventoryModel.CreateInventory($scope.data.inventory_name).then(function(inventory_id){
                $rootScope.currentInventoryId = inventory_id;
                $state.go('select_stock_location');
            });
        } else {
            $scope.errorMessage = $translate.instant("Inventory Name Required");
        }
    };
}]);
