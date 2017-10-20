"use strict";
angular.module('mobile_app_inventory').controller(
        'SelectStockInventoryCtrl', [
        '$scope', '$rootScope', '$state', 'StockInventoryModel', '$translate',
        function ($scope, $rootScope, $state, StockInventoryModel, $translate) {

    $scope.data = {
        'inventories': [],
    };

    $scope.$on(
            '$stateChangeSuccess',
            function(event, toState, toParams, fromState, fromParams){
        if ($state.current.name === 'inventory') {
            StockInventoryModel.get_list().then(function (inventories) {
                $scope.data.inventories = inventories;
            });
            $scope.data.inventory_name = '';
        }
    });

    $scope.select_inventory = function (inventory_id) {
        console.log("selectInventory", inventory_id);
        $state.go('location', {
            inventory_id: inventory_id
        });
    };

    $scope.submit = function () {
        if ($scope.data.inventory_name !== '') {
            StockInventoryModel.CreateInventory($scope.data.inventory_name).then(function(inventory){
                console.log("RESULT CREATE");
                console.log(inventory);
                $scope.select_inventory(inventory.id)
            });
        } else {
            $scope.errorMessage = $translate.instant("Inventory Name Required");
        }
    };
}]);
