"use strict";
angular.module('mobile_app_inventory').controller(
        'ConfirmQuantityCtrl',
        ['$scope', '$state', 'StockInventoryModel', '$translate',
        function ($scope, $state, StockInventoryModel, $translate) {

    $scope.data = {
        'inventory_id': false,
        'location_id': false,
        'product_id': false,
        'current_qty': 0,
        'new_qty': 0,
        'sum_qty': 0,
    };

    $scope.$on(
            '$stateChangeSuccess',
            function(event, toState, toParams, fromState, fromParams){
        if ($state.current.name === 'confirm_quantity') {
            // Get Product Data
            $scope.data.inventory_id = parseInt(toParams.inventory_id, 10);
            $scope.data.location_id = parseInt(toParams.location_id, 10);
            $scope.data.product_id = parseInt(toParams.product_id, 10);
            $scope.data.current_qty = parseInt(toParams.current_qty, 10);
            $scope.data.new_qty = parseInt(toParams.new_qty, 10);
            $scope.data.sum_qty = $scope.data.current_qty + $scope.data.new_qty;
        }
    });

    $scope._set_quantity = function(mode) {
        StockInventoryModel.add_inventory_line(
                 $scope.data.inventory_id, $scope.data.location_id,
                $scope.data.product_id, $scope.data.new_qty, mode).then(function (res){
            if (res.state == 'write_ok'){
                angular.element(document.querySelector('#sound_quantity_selected'))[0].play();
                setTimeout(function(){
                    $state.go('product', {
                        inventory_id: $scope.data.inventory_id,
                        location_id: $scope.data.location_id,
                    });
                }, 300);
            }else {
                $scope.errorMessage = $translate.instant("Too Many Duplicate Lines");
                angular.element(document.querySelector('#sound_user_error'))[0].play();
            }
        }, function(reason) {
            $scope.errorMessage = $translate.instant("Something Wrong Happened");
        });

    };

    $scope.add_quantity = function () {
        $scope._set_quantity('add');
    };

    $scope.replace_quantity = function () {
        $scope._set_quantity('replace');
    };

}]);
