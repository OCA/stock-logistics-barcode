"use strict";
angular.module('mobile_app_inventory').controller(
        'ProductCtrl', [
        '$scope', '$state', '$translate', 'InventoryModel', 'LocationModel', 'ProductModel', 'SettingModel',
        function ($scope, $state, $translate, InventoryModel, LocationModel, ProductModel, SettingModel) {

    $scope.data = { };

    $scope.$on(
            '$stateChangeSuccess',
            function(event, toState, toParams, fromState, fromParams){
        if ($state.current.name === 'product') {
            // Set Focus
            angular.element(document.querySelector('#input_ean13'))[0].focus();
            //Initialize default data
            $scope.data.ean13 = '';
            $scope.errorMessage = "";
            // Get Inventory / Location Data
            InventoryModel.get_inventory(toParams.inventory_id).then(function (inventory) {
                $scope.inventory = inventory;
            });
            LocationModel.get_location(toParams.location_id).then(function (location) {
                $scope.location = location;
            });
        }
    });

    $scope.submit = function () {
        // Reset Focus, in case the barcode is not correct
        angular.element(document.querySelector('#input_ean13'))[0].focus();
        if ($scope.data.ean13) {
            ProductModel.search_product($scope.data.ean13).then(function (product) {
                SettingModel.get_setting('inventory_allow_unknown').then(function (setting) {
                    if (!product.found && !setting){
                        $scope.errorMessage = $translate.instant("Unknown EAN13 Barcode");
                        angular.element(document.querySelector('#sound_error'))[0].play();
                    } else {
                        $state.go('quantity', {
                            inventory_id: $scope.inventory.id,
                            location_id: $scope.location.id,
                            ean13: product.barcode,
                        });
                    }
                });
            });
        } else {
            $scope.errorMessage = $translate.instant("Barcode : Required field");
            angular.element(document.querySelector('#sound_error'))[0].play();
       }
    };

}]);
