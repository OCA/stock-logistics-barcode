"use strict";
angular.module('mobile_app_inventory').controller(
        'SelectStockInventoryCtrl', [
        '$scope', '$state', 'ResCompanyModel', 'StockInventoryModel', 'ProductProductModel', '$translate',
        function ($scope, $state, ResCompanyModel, StockInventoryModel, ProductProductModel, $translate) {

    $scope.data = {
        'inventories': [],
        'mobile_inventory_create': false,
    };

    $scope.$on(
            '$stateChangeSuccess',
            function(event, toState, toParams, fromState, fromParams){
        if ($state.current.name === 'inventory') {
            $scope.data.inventory_name = '';
            StockInventoryModel.get_list(false).then(function (inventories) {
                $scope.data.inventories = inventories;
            });
            ResCompanyModel.get_setting('mobile_inventory_create').then(function (setting) {
                $scope.data.mobile_inventory_create = setting;
            });
        }
    });

    $scope.submit = function () {
        if ($scope.data.inventory_name !== '') {
            StockInventoryModel.create_inventory($scope.data.inventory_name).then(function(inventory){
                $scope.select_inventory(inventory.id);
            });
        } else {
            $scope.errorMessage = $translate.instant("Inventory Name Required");
        }
    };

    $scope.select_inventory = function (inventory_id) {
        ResCompanyModel.get_setting('mobile_product_cache').then(function (setting) {
            if (setting == 'inventory'){
                // Cache products of the inventory lines
                console.log("loading by inventory");
                ProductProductModel.get_list(true, inventory_id).then(function(product_list) {
                    $state.go('location', {inventory_id: inventory_id});
                });
            }
            else {
                $state.go('location', {inventory_id: inventory_id});
            }
        });

    };

}]);
