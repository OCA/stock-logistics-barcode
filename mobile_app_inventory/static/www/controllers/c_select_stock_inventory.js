"use strict";
angular.module('mobile_app_inventory').controller(
        'SelectStockInventoryCtrl', [
        '$scope', '$rootScope', '$state', 'StockInventoryModel', '$translate',
        function ($scope, $rootScope, $state, StockInventoryModel, $translate) {

    console.log("coincoin");
    $scope.data = {
        'inventories': [],
    };
    StockInventoryModel.get_list().then(function (inventories) {
        $scope.data.inventories = inventories;
    });

    $scope.$on(
            '$stateChangeSuccess',
            function(event, toState, toParams, fromState, fromParams){
        if ($state.current.name === 'select_stock_inventory') {
            console.log("c_select_stock_inventory::stateChangeSuccess");
            $scope.data.inventory_name = '';
        }
    });

    $scope.selectInventory = function (inventory_id, inventory_name) {
        $rootScope.currentInventoryId = inventory_id;
        $rootScope.currentInventoryName = inventory_name;
        $state.go('location', {
            inventory_id: inventory_id
        });
    };

    $scope.submit = function () {
        if ($scope.data.inventory_name !== '') {
            StockInventoryModel.CreateInventory($scope.data.inventory_name).then(function(inventory){
                console.log("RESULT CREATE");
                console.log(inventory);
                $scope.selectInventory(inventory.id, inventory.name)
            });
        } else {
            $scope.errorMessage = $translate.instant("Inventory Name Required");
        }
    };
}]);
