"use strict";
angular.module('mobile_app_inventory').controller(
        'SelectStockInventoryCtrl', [
        '$scope', '$rootScope', '$state', 'StockInventoryModel', '$translate',
        function ($scope, $rootScope, $state, StockInventoryModel, $translate) {
    console.log('dans stock inventory ctrl')
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
        console.log('dans stock inventory stateChangeSuccess', $state.current)

        if ($state.current.name === 'select_stock_inventory') {
            $scope.data.inventory_name = '';
        }
    });

    $scope.selectInventory = function (inventory_id) {
        console.log('dans selectInventory', inventory_id)
        $rootScope.currentInventoryId = inventory_id;
        $state.go('location', {
            inventory_id: inventory_id
        });
    };

    $scope.submit = function () {
        if ($scope.data.inventory_name !== '') {
            StockInventoryModel.CreateInventory($scope.data.inventory_name).then(function(inventory_id){
                $scope.selectInventory(inventory_id)
            });
        } else {
            $scope.errorMessage = $translate.instant("Inventory Name Required");
        }
    };
}]);
