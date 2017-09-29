"use strict";
angular.module('mobile_app_inventory').controller(
        'LoadCtrl', [
        '$q', '$scope', '$rootScope', 'jsonRpc', '$state', 'ProductProductModel', 'StockLocationModel', 'StockInventoryModel', '$translate',
        function ($q, $scope, $rootScope, jsonRpc, $state, ProductProductModel, StockLocationModel, StockInventoryModel, $translate) {

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

            $q.all([
                ProductProductModel.LoadProductList().then( qty => {
                    $scope.data.product_load_state = true;
                    $scope.data.product_qty = qty;
                }),
                StockLocationModel.LoadLocationList().then(qty => {
                    $scope.data.location_load_state = true;
                    $scope.data.location_qty = qty;
                }),
                StockInventoryModel.LoadDraftInventoryList().then(qty => {
                    $scope.data.inventory_load_state = true;
                    $scope.data.inventory_qty = qty;
                })
            ]).then(
                () => {
                    // Display OK message, when all data are loaded and go to the next page
                    $scope.doneMessage = $translate.instant('Loading Done');
                    setTimeout(function(){
                        $state.go('select_stock_inventory');
                    }, 1000);
                }, () => {
                    $scope.loadingMessage = "";
                    $scope.doneMessage = "";
                    $scope.errorMessage = $translate.instant("Loading Failed");
                    angular.element(document.querySelector('#sound_loading_failed'))[0].play();
                }
            );
        }
    });

}]);
