"use strict";
angular.module('mobile_app_inventory').controller(
    'MainScanCtrl', [
    '$scope', '$state', '$q', '$timeout', '$translate','scan_state', 'InventoryModel', 'LocationModel', 'ProductModel',
    function ($scope, $state, $q, $timeout, $translate, scan_state, InventoryModel, LocationModel, ProductModel) {

    $scope.placeholder = "Barcode of product or location"
    scan_state.set_callback(function (data) {
        //called when a product has been sent 
        return InventoryModel.add_inventory_line(
            data.inventory, data.location,
            data.product, data.qty,
            'ask').then(function success(ret) {

            if (ret.state == 'duplicate') {
                $state.go('confirm_quantity', {
                    inventory_id: data.inventory.id,
                    location_id: data.location.id,
                    product_id: data.product.id,
                    current_qty: ret.qty,
                    new_qty: data.qty
                });
            } else if (ret.state == 'write_ok') {
                $scope.successMessage = $translate.instant("Saved");
                $timeout(function () {
                    $scope.successMessage = "";
                }, 2000);
            }
            return ret;
        }).then(null, function error(err) {
            $scope.errorMessage = $translate.instant(err.fullTrace.data.message);
            $timeout(function() {
                scan_state.reset(); //reset after few seconds
            }, 3000);
            return $q.reject(err);
        });
    });
    $scope.data = scan_state.get_data();
    $scope.input = {};

    $scope.$on(
        '$stateChangeSuccess',
        function(event, toState, toParams, fromState, fromParams){
        if ($state.current.name === 'product') {
            // Set Focus
            angular.element(document.querySelector('#input_ean13'))[0].focus();
            
            LocationModel.get_location(toParams.location_id).then(function (location) {
                scan_state.set_location(location);
            });
            InventoryModel.get_inventory(toParams.inventory_id).then(function(inventory) {
                scan_state.set_inventory(inventory);
            });
        }
    });

    $scope.submit = function (input) {
        //input is string
        //input can be a location (barcode), a product (barcode), a quantity
        if ($scope.errorMessage) {
            //reset scan_state to stable state
            scan_state.reset();
        }
        $scope.errorMessage = "";
        $scope.successMessage = "";
        
        function is_barcode(input) {
            return ('' + input).length > 5;
        }

        if (is_barcode(input)) {
            //try with location first
            //because it's always in cache and the lookup is quick
            var barcode = '' + input; //force cast to preseve trailling 0
            var location = LocationModel.search_location(barcode);
            if (location) {
                scan_state.set_location(location);
            } else {
                //it's a product known or unkown
                ProductModel.search_product(barcode).then(function (product) {
                    scan_state.set_product(product);
                });
            }
        } else {
            // is qty
            var qty = parseFloat(input);
            if (!qty) {
                $scope.errorMessage = $translate.instant("Wrong barcode or quantity");
            } else {
                scan_state.set_qty(qty).then(function (a) {
                    //TODO display warning if != expected quantity ?
                }).then(function (msg) {
                    $scope.errorMessage = $translate.instant(msg);
                });
            }
        }
        $scope.input = {}; //reset field
    };
}]).directive('toggleAnim', ['$timeout', function($timeout) {
    return {
        scope: { 'toggleAnim':'='},
        template: '',
        link: function ($scope, elem, attrs) { 
            //alter background when the value change
            $scope.$watch('toggleAnim', function(after, before) {
                elem.toggleClass('item-divider');
            });
        }
    };
}]);
