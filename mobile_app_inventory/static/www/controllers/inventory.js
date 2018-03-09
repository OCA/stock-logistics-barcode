"use strict";
angular.module('mobile_app_inventory').controller(
    'InventoryCtrl', [
        '$scope', '$state', 'scan_state', 'SettingModel', 'InventoryModel', 'ProductModel', '$translate',
        function ($scope, $state, scan_state, SettingModel, InventoryModel, ProductModel, $translate) {

    $scope.data = {
        'inventory_list': [],
        'inventory_filter': null,
        'mobile_inventory_create': false,
    };

    $scope.$on(
        '$stateChangeSuccess',
        function(event, toState, toParams, fromState, fromParams){
        if ($state.current.name === 'inventory') {
            $scope.data.inventory_filter = null;
            InventoryModel.get_list().then(function (inventory_list) {
                $scope.data.inventory_list = inventory_list;
            });
            SettingModel.get_setting('inventory_create').then(function (setting) {
                $scope.data.mobile_inventory_create = setting;
            });
        }
    });

    $scope.submit = function () {
        InventoryModel.create_inventory($scope.data.inventory_filter).then(function(inventory){
            scan_state.set_inventory(inventory);
            $scope.select_inventory(inventory.id);
        });
    };

    $scope.select_inventory = function (inventory_id) {
        ProductModel.get_list({id:inventory_id}).then(function(product_list) {
            $state.go('location', {inventory_id: inventory_id});
        });
    };

}]);
