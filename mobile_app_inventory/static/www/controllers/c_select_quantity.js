"use strict";
angular.module('mobile_app_inventory').controller(
        'SelectQuantityCtrl',
        ['$scope', '$rootScope', 'jsonRpc', '$state','$translate',
         'StockInventoryModel', 'ProductProductModel',
        function ($scope, $rootScope, jsonRpc, $state, $translate
            StockInventoryModel, ProductProductModel) {

    $scope.data = {
        'qty': '',
    };

    $scope.$on(
            '$stateChangeSuccess',
            function(event, toState, toParams, fromState, fromParams){
        if ($state.current.name === 'select_quantity') {
            // Set Focus
            angular.element(document.querySelector('#input_quantity'))[0].focus();
            $scope.data.qty = '';
            // Get Product Data
            $scope.product = null;
            return ProductProductModel.get_product(toParams).then(function (product) {
                $scope.product = product;
            });
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

        StockInventoryModel.AddInventoryLine(
                $rootScope.currentInventoryId,
                $rootScope.currentLocationId, $scope.product.id,
                parsed_qty, 'ask').then(function (res){
            if (res.state == 'write_ok'){
                angular.element(document.querySelector('#sound_quantity_selected'))[0].play();
                setTimeout(function(){
                    $state.go('select_product_product');
                }, 300);
            }else {
                if (res.state == 'duplicate'){
                    $state.go('confirm_quantity', {
                        product_id: $scope.product.id,
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
