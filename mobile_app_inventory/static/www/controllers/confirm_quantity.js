"use strict";
angular.module('mobile_app_inventory').controller(
        'ConfirmQuantityCtrl',
        ['$scope', '$state', 'InventoryModel', 'ProductModel', 'tools', '$translate',
        function ($scope, $state, InventoryModel, ProductModel, tools, $translate) {

    $scope.data = { }

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
            $scope.data.product = ProductModel.get_product($scope.data.product_id);
        }
    });

    $scope._set_quantity = function(mode) {
        InventoryModel.add_inventory_line(
            {id: $scope.data.inventory_id},
            {id: $scope.data.location_id},
            {id: $scope.data.product_id},
            $scope.data.new_qty, mode
        ).then(function (res){
            if (res.state == 'write_ok'){
                angular.element(document.querySelector('#sound_ok'))[0].play();
                tools.go_to_scan_page($scope.data.inventory_id, $scope.data.location_id);
            } else {
                $scope.errorMessage = $translate.instant("Too Many Duplicate Lines");
                angular.element(document.querySelector('#sound_error'))[0].play();
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

    $scope.reset = function() {
        tools.go_to_scan_page($scope.data.inventory_id, $scope.data.location_id);
    };

}]);
