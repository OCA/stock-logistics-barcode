"use strict";
angular.module('mobile_app_inventory').controller(
        'QuantityCtrl',
        ['$scope', '$state', '$translate', 'InventoryModel', 'LocationModel', 'ProductModel', 'tools',
        function ($scope, $state, $translate, InventoryModel, LocationModel, ProductModel, tools) {

    $scope.data = { };

    $scope.$on(
            '$stateChangeSuccess',
            function(event, toState, toParams, fromState, fromParams){
        if ($state.current.name === 'quantity') {
            // Set Focus
            angular.element(document.querySelector('#input_quantity'))[0].focus();

            //Initialize default data
            $scope.errorMessage = '';
            $scope.data.qty = '';
            // Get Inventory / Location / Product Data
            InventoryModel.get_inventory(toParams.inventory_id).then(function (inventory) {
                $scope.inventory = inventory;
            });
            LocationModel.get_location(toParams.location_id).then(function (location) {
                $scope.location = location;
            });
            ProductModel.search_product(toParams.ean13).then(function (product) {
                if (product.barcode_qty){
                    $scope.data.qty = product.barcode_qty;
                }
                $scope.product = product;
            });
        }
    });

    $scope.submit = function () {
        // Reset Focus, in case the quantity is not correct
        angular.element(document.querySelector('#input_quantity'))[0].focus();
        var parsed_qty = parseInt($scope.data.qty);
        if (! isNaN(parsed_qty)){
            if (parsed_qty < 1000000){
                InventoryModel.add_inventory_line(
                    $scope.inventory, $scope.location, $scope.product,
                        parsed_qty, 'ask').then(function (res){
                    if (['write_ok', 'unknown_barcode_added'].indexOf(res.state) >= 0){
                        angular.element(document.querySelector('#sound_ok'))[0].play();
                        tools.go_to_scan_page($scope.inventory.id, $scope.location.id);
                    }else {
                        if (res.state === 'duplicate'){
                            $state.go('confirm_quantity', {
                                inventory_id: $scope.inventory.id,
                                location_id: $scope.location.id,
                                product_id: $scope.product.id,
                                current_qty: res.qty,
                                new_qty: parsed_qty});
                        } else if (res.state === 'many_duplicate_lines'){
                            $scope.errorMessage = $translate.instant("Too Many Duplicate Lines");
                            angular.element(document.querySelector('#sound_error'))[0].play();
                        } else if (res.state === 'user_error'){
                            $scope.errorMessage = res.message;
                            angular.element(document.querySelector('#sound_error'))[0].play();
                        }
                    }
                }, function(reason) {
                    $scope.errorMessage = $translate.instant("Something Wrong Happened");
                });
            }else{
                $scope.errorMessage = $translate.instant("Too Big Quantity");
                angular.element(document.querySelector('#sound_error'))[0].play();
            }
        }
        else{
            $scope.errorMessage = $translate.instant("Incorrect Quantity");
            angular.element(document.querySelector('#sound_error'))[0].play();
        }
    };

    $scope.reset = function() {
        tools.go_to_scan_page($scope.inventory.id, $scope.location.id);
    };

}]);
