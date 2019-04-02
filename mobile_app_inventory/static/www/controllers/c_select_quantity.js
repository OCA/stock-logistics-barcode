"use strict";
angular.module('mobile_app_inventory').controller(
        'SelectQuantityCtrl',
        ['$scope', '$state', '$translate', 'InventoryModel', 'LocationModel', 'ProductProductModel',
        function ($scope, $state, $translate, InventoryModel, LocationModel, ProductProductModel) {

    $scope.data = {
        'inventory': false,
        'location': false,
        'fixed_qty': false,
        'qty': '',
        'product': '',
    };

    $scope.$on(
            '$stateChangeSuccess',
            function(event, toState, toParams, fromState, fromParams){
        if ($state.current.name === 'product_ean13') {
            InventoryModel.get_inventory(parseInt(toParams.inventory_id, 10)).then(function (inventory) {
                $scope.data.inventory = inventory;
            });
            LocationModel.get_location(parseInt(toParams.location_id, 10)).then(function (location) {
                $scope.data.location = location;
            });
            $scope.data.fixed_qty = false;
            ProductProductModel.get_product(toParams.ean13).then(function(product) {
                if (product['barcode_qty'] !== undefined) {
                    $scope.data.fixed_qty = true;
                    $scope.data.qty = parseFloat(product['barcode_qty']);
                }
                $scope.data.product = product;
            });
            angular.element(document.querySelector('#input_quantity'))[0].focus();
            $scope.data.qty = '';
        }
    });

    $scope.submit = function () {
        var parsed_qty = parseInt($scope.data.qty);
        $scope.errorMessage = '';
        if (!parsed_qty || parsed_qty < 0) {
            $scope.errorMessage = $translate.instant("Incorrect Quantity");
            angular.element(document.querySelector('#sound_user_error'))[0].play();
            return;
        }
        if (parsed_qty > 1000000) { // may be an ean13
            $scope.errorMessage = $translate.instant("Too Big Quantity");
            angular.element(document.querySelector('#sound_user_error'))[0].play();
            return;
        }

        InventoryModel.add_inventory_line(
                $scope.data.inventory.id, $scope.data.location.id,
                $scope.data.product.id, parsed_qty, 'ask').then(function (res){
            if (res.state == 'write_ok'){
                angular.element(document.querySelector('#sound_quantity_selected'))[0].play();
                $state.go('product', {
                        'inventory_id': $scope.data.inventory.id,
                        'location_id': $scope.data.location.id
                });
            }else {
                if (res.state == 'duplicate'){
                    $state.go('confirm_quantity', {
                        inventory_id: $scope.data.inventory.id,
                        location_id: $scope.data.location.id,
                        product_id: $scope.data.product.id,
                        current_qty: res.qty,
                        new_qty: parsed_qty});
                } else {
                    $scope.errorMessage = $translate.instant("Too Many Duplicate Lines");
                    angular.element(document.querySelector('#sound_user_error'))[0].play();
                }
            }
        }, function(reason) {
            $scope.errorMessage = $translate.instant("Something Wrong Happened");
        });
    };
}]);
