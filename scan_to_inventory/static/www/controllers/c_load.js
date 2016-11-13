angular.module('scan_to_inventory').controller(
        'LoadCtrl', [
        '$scope', '$rootScope', 'jsonRpc', '$state', 'ProductProductModel', 'StockLocationModel', 'StockInventoryModel', '$translate',
        function ($scope, $rootScope, jsonRpc, $state, ProductProductModel, StockLocationModel, StockInventoryModel, $translate) {

    $scope.data = {};

    $scope.$on(
            '$stateChangeSuccess',
            function(event, toState, toParams, fromState, fromParams){
        if ($state.current.name === 'load') {
            $scope.data.product_ok = false;
            $scope.data.product_ko = false;
            $scope.data.location_ok = false;
            $scope.data.location_ko = false;
            $scope.data.inventory_ok = false;
            $scope.data.inventory_ko = false;

            $scope.loadingMessage = $translate.instant("Pending Loading ...");
            $scope.doneMessage = "";
            $scope.errorMessage = "";

            ProductProductModel.LoadProductList().then(function(product_qty){
                $scope.data.product_ok = true;
                $scope.data.product_qty = product_qty;
                StockLocationModel.LoadLocationList().then(function(location_qty){
                    $scope.data.location_ok = true;
                    $scope.data.location_qty = location_qty;
                    StockInventoryModel.LoadDraftInventoryList().then(function(inventory_qty){
                        $scope.data.inventory_ok = true;
                        $scope.data.inventory_qty = inventory_qty;
                        $scope.doneMessage = $translate.instant("Loading Done");
                        setTimeout(function(){
                            $state.go('select_stock_inventory');
                        }, 1000);
                    }, function(reason) {
                        $scope.LoadingError();
                    });
                }, function(reason) {
                    $scope.LoadingError();
                });
            }, function(reason) {
                $scope.LoadingError();
            });
        }
    });

    $scope.LoadingError = function () {
        $scope.loadingMessage = "";
        $scope.doneMessage = "";
        $scope.errorMessage = $translate.instant("Loading Failed");
        angular.element(document.querySelector('#sound_loading_failed'))[0].play();
    };

}]);
