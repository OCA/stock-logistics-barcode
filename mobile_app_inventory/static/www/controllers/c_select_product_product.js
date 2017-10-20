"use strict";
angular.module('mobile_app_inventory').controller(
        'SelectProductProductCtrl', [
        '$scope', '$rootScope', '$state', '$translate',
        'StockInventoryModel', 'StockLocationModel', 'ProductProductModel',
        function ($scope, $rootScope, $state, $translate,
            StockInventoryModel, StockLocationModel, ProductProductModel) {

    $scope.data = {
        'ean13': '',
        'location': null,
        'parent_complete_name': '',
    };

    $scope.$on(
        '$stateChangeSuccess',
        function(event, toState, toParams, fromState, fromParams){
        // Set Focus
        angular.element(document.querySelector('#input_ean13'))[0].focus();
        $scope.data.ean13 = '';
        StockLocationModel.get_location(toParams.location_id).then(function (location) {
            $scope.data.location = location;
        })
        StockInventoryModel.get_inventory(toParams.inventory_id).then(function(inventory) {
            $scope.data.inventory = inventory;
        });
    });

    $scope.submit = function () {
        $scope.errorMessage = "";
        return ProductProductModel.get_product($scope.data.ean13).then(function success() {
            var ret = $state.go('product_ean13', {
                inventory_id: $scope.data.inventory.id,
                location_id: $scope.data.location.id,
                ean13: $scope.data.ean13});
        }, function error(msg) {
            $scope.errorMessage = $translate.instant("Unknown EAN13 Barcode");
            angular.element(document.querySelector('#sound_user_error'))[0].play();
        });
    };

}]);
