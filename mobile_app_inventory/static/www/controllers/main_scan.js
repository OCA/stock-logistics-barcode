"use strict";
angular.module('mobile_app_inventory').controller(
    'MainScanCtrl', [
    '$scope', '$state', '$q', '$timeout', '$translate','scan_state', 'InventoryModel', 'LocationModel', 'ProductModel',
    function ($scope, $state, $q, $timeout, $translate, scan_state, InventoryModel, LocationModel, ProductModel) {

    function display_error(msg) {
        $scope.errorMessage = msg;
        angular.element(document.querySelector('#sound_user_error'))[0].play();
        var before = scan_state.get_data();
        $timeout(function() {
            $scope.errorMessage = '';
            if (before == scan_state.get_data())
                scan_state.reset(); //reset if user didn't change a thing
        }, 3000);
    }
    function display_success(msg) {
        $scope.successMessage = msg;
        angular.element(document.querySelector('#sound_quantity_selected'))[0].play();
          $timeout(function () {
            $scope.successMessage = "";
        }, 2000);
    }


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
            } else if (ret.state == 'write_ok' || ret.state == 'unknown_barcode_added') {
                display_success($translate.instant("Saved"));
            }
            return ret;
        }).then(null, function error(err) {
            display_error($translate.instant(err.fullTrace.data.message));
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
        if (!input) {
            //may the user want to force the submission now ? 
            scan_state.add_inventory_line();
        } else if (is_barcode(input)) {
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
                }).then(null, function (msg) {
                    display_error($translate.instant(msg));
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
