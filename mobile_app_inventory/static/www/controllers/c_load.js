"use strict";
angular.module('mobile_app_inventory').controller(
        'LoadCtrl', [
        '$q', '$scope', '$state', 'ResCompanyModel', 'ProductProductModel', 'StockLocationModel', 'StockInventoryModel', '$translate',
        function ($q, $scope, $state, ResCompanyModel, ProductProductModel, StockLocationModel, StockInventoryModel, $translate) {

    $scope.data = {};

    $scope.$on(
            '$stateChangeSuccess',
            function(event, toState, toParams, fromState, fromParams){
        if ($state.current.name === 'load') {
            $scope.data.product_qty = 0;
            $scope.data.product_load_state = undefined;
            $scope.data.location_qty = 0;
            $scope.data.location_load_state = undefined;
            $scope.data.inventory_qty = 0;
            $scope.data.inventory_load_state = undefined;

            $scope.loadingMessage = $translate.instant("Pending Loading ...");
            $scope.doneMessage = "";
            $scope.errorMessage = "";
            window.products = ProductProductModel;

            $q.all([
                // TODO  call product get_list, only if 
//                ResCompanyModel.get_setting('mobile_product_cache').then(function (setting) {
//                    $scope.data.mobile_inventory_create = setting;
//                });

                ProductProductModel.get_list(true, false).then(function (products) {
                    $scope.data.product_load_state = true;
                    $scope.data.product_qty = Object.keys(products).length;
                }),
                StockLocationModel.get_list(true).then(function (locations) {
                    $scope.data.location_load_state = true;
                    $scope.data.location_qty = locations.length;
                }),
                StockInventoryModel.get_list(true).then(function (inventories) {
                    $scope.data.inventory_load_state = true;
                    $scope.data.inventory_qty = inventories.length;
                })
            ]).then(
                function () {
                    // Display OK message, when all data are loaded and go to the next page
                    $scope.doneMessage = $translate.instant('Loading Done');
                    setTimeout(function(){
                        $state.go('inventory');
                    }, 1000);
                }, function() {
                    $scope.loadingMessage = "";
                    $scope.doneMessage = "";
                    $scope.errorMessage = $translate.instant("Loading Failed");
                    angular.element(document.querySelector('#sound_loading_failed'))[0].play();
                }
            );
        }
    });

}]);
