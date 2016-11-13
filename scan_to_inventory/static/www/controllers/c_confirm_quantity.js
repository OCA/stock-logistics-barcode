'use strict';


angular.module('scan_to_inventory').controller(
        'ConfirmQuantityCtrl',
        ['$scope', '$rootScope', 'jsonRpc', '$state', 'StockInventoryModel', '$translate',
        function ($scope, $rootScope, jsonRpc, $state, StockInventoryModel, $translate) {

    $scope.data = {
        'product_id': 0,
        'current_qty': 0,
        'new_qty': 0,
        'sum_qty': 0,
    };

    $scope.$on(
            '$stateChangeSuccess',
            function(event, toState, toParams, fromState, fromParams){
        if ($state.current.name === 'confirm_quantity') {
            // Get Product Data
            $scope.data.product_id = parseInt(toParams['product_id']);
            $scope.data.current_qty = parseInt(toParams['current_qty']);
            $scope.data.new_qty = parseInt(toParams['new_qty']);
            $scope.data.sum_qty = $scope.data.current_qty + $scope.data.new_qty;
        }
    });

    // TODO
    // Refactor me. merge add_quantity and replace_quantity code
    $scope.add_quantity = function () {
        StockInventoryModel.AddInventoryLine(
                $rootScope.currentInventoryId,
                $rootScope.currentLocationId, $scope.data.product_id,
                $scope.data.sum_qty, 'add').then(function (res){
            if (res['state'] == 'write_ok'){
                angular.element(document.querySelector('#sound_quantity_selected'))[0].play();
                setTimeout(function(){
                    $state.go('select_product_product');
                }, 300);
            }else {
                $scope.errorMessage = $translate.instant("Too Many Duplicate Lines");
                angular.element(document.querySelector('#sound_user_error'))[0].play();
            }
        }, function(reason) {
            $scope.errorMessage = $translate.instant("Something Wrong Happened");
        });
    };

    $scope.replace_quantity = function () {
        StockInventoryModel.AddInventoryLine(
                $rootScope.currentInventoryId,
                $rootScope.currentLocationId, $scope.data.product_id,
                $scope.data.new_qty, 'replace').then(function (res){
            if (res['state'] == 'write_ok'){
                angular.element(document.querySelector('#sound_quantity_selected'))[0].play();
                setTimeout(function(){
                    $state.go('select_product_product');
                }, 300);
            }else {
                $scope.errorMessage = $translate.instant("Too Many Duplicate Lines");
                angular.element(document.querySelector('#sound_user_error'))[0].play();
            }
        }, function(reason) {
            $scope.errorMessage = $translate.instant("Something Wrong Happened");
        });
    };

}]);
