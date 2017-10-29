"use strict";
angular.module('mobile_app_inventory').controller(
        'SelectInventoryCtrl', [
        '$scope', '$state', 'SettingModel', 'InventoryModel', 'ProductProductModel', '$translate',
        function ($scope, $state, SettingModel, InventoryModel, ProductProductModel, $translate) {

    $scope.data = {
        'inventory_list': [],
        'mobile_inventory_create': false,
    };

    $scope.$on(
            '$stateChangeSuccess',
            function(event, toState, toParams, fromState, fromParams){
        if ($state.current.name === 'inventory') {
            $scope.data.inventory_name = '';
            InventoryModel.get_list(false).then(function (inventory_list) {
                $scope.data.inventory_list = inventory_list;
            });
            SettingModel.get_setting('inventory_create').then(function (setting) {
                $scope.data.mobile_inventory_create = setting;
            });
        }
    });

    $scope.submit = function () {
        if ($scope.data.inventory_name !== '') {
            InventoryModel.create_inventory($scope.data.inventory_name).then(function(inventory){
                $scope.select_inventory(inventory.id);
            });
        } else {
            $scope.errorMessage = $translate.instant("Inventory Name Required");
        }
    };

    $scope.select_inventory = function (inventory_id) {
        SettingModel.get_setting('mobile_product_cache').then(function (setting) {
            if (setting == 'inventory'){
                // Cache products of the inventory lines
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
