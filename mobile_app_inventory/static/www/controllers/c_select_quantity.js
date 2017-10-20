"use strict";
angular.module('mobile_app_inventory').controller(
        'SelectQuantityCtrl',
        ['$scope', '$rootScope', '$state', '$translate',
         'StockInventoryModel', 'StockLocationModel', 'ProductProductModel',
        function ($scope, $rootScope, $state, $translate,
            StockInventoryModel, StockLocationModel, ProductProductModel) {

    $scope.data = {
        'qty': '',
        'product': '',
        'location': '',
    };

    $scope.$on(
        '$stateChangeSuccess',
        function(event, toState, toParams, fromState, fromParams){
        StockLocationModel.get_location(toParams.location_id).then(function (location) {
            $scope.data.location = location;
        })
        StockInventoryModel.get_inventory(toParams.inventory_id).then(function(inventory) {
            $scope.data.inventory = inventory;
        });
        ProductProductModel.get_product(toParams.ean13).then(function(product) {
            $scope.data.product = product;
        });
        angular.element(document.querySelector('#input_quantity'))[0].focus();
        $scope.data.qty = '';
        console.log($scope);
        // Get Product Data
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

        StockInventoryModel.AddInventoryLine(
                $scope.data.inventory.id,
                $scope.data.location.id,
                $scope.data.product.id,
                parsed_qty, 'ask').then(function (res){
            if (res.state == 'write_ok'){
                angular.element(document.querySelector('#sound_quantity_selected'))[0].play();
                $state.go('product', {
                        'inventory_id': $scope.data.inventory.id,
                        'location_id': $scope.data.location.id
                });
            }else {
                if (res.state == 'duplicate'){
                    $state.go('confirm_quantity', {
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
