"use strict";
angular.module('mobile_app_inventory').controller(
        'SelectProductProductCtrl', [
        '$scope', '$state', '$translate', 'InventoryModel', 'LocationModel', 'ProductProductModel',
        function ($scope, $state, $translate, InventoryModel, LocationModel, ProductProductModel) {

    fsm.set_service(InventoryModel);
    $scope.data = fsm.get_data();
    $scope.input = {};

    $scope.$on(
            '$stateChangeSuccess',
            function(event, toState, toParams, fromState, fromParams){
        if ($state.current.name === 'product') {
            // Set Focus
            angular.element(document.querySelector('#input_ean13'))[0].focus();
            $scope.data.ean13 = '';
            LocationModel.get_location(parseInt(toParams.location_id, 10)).then(function (location) {
                console.log(location);
                $scope.data.location = location;
                fsm.set_location(location);
            })
            InventoryModel.get_inventory(toParams.inventory_id).then(function(inventory) {
                $scope.data.inventory = inventory;
                fsm.set_inventory(inventory);
            });
        }
    });

    $scope.submit = function (input) {
        $scope.errorMessage = "";
        //input should be string
        console.log('input', input);
        function is_barcode(input) {
            return ('' + input).length > 5;
        }

        function get_location(input) {
            console.log('get location', input);
            return LocationModel.search_location(input);
        }
        function get_product(input) {
            console.log('get product', input);
            return ProductProductModel.get_product(input);
        }

        //try with location first
        if (is_barcode(input)) {
            var barcode = '' + input;
            var location = get_location(barcode);
            if (location) {
                fsm.set_location(location);
            } else {
                get_product(barcode).then(function (product) {
                    fsm.set_product(product);
                });
            }
        } else {
            console.log('dans set qty');
            // is qty
            var qty = parseFloat(input);
            if (!qty)
                throw "Wrong qty";
            fsm.set_qty(qty);
        }

        console.log(fsm.get_data());
        $scope.input = {};
        return;
        return LocationModel.search_location($scope.data.ean13).then(
            function (location) {
                console.log('on a scanné un emplacement !');
                $scope.data.location = location;
                $scope.data.ean13 = null;
            }, function (error) {
                //then try with product #TODO refactore in a signal Model
                return ProductProductModel.get_product($scope.data.ean13).then(
                    function(product) {
                        return $state.go('product_ean13', {
                            inventory_id: $scope.data.inventory.id,
                            location_id: $scope.data.location.id,
                            ean13: $scope.data.ean13});
                    }
                );
            }).then(null, function (error) {
                $scope.errorMessage = $translate.instant("Unknown EAN13 Barcode");
                angular.element(document.querySelector('#sound_user_error'))[0].play();
            });
    };

}]);
