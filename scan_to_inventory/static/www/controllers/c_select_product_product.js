angular.module('scan_to_inventory').controller(
        'SelectProductProductCtrl', [
        '$scope', '$rootScope', 'jsonRpc', '$state', '$translate', 'StockInventoryModel',
        function ($scope, $rootScope, jsonRpc, $state, $translate, StockInventoryModel) {

    $scope.data = {
        'ean13': '',
        'location_name': '',
        'parent_complete_name': '',
    };

    $scope.$on(
            '$stateChangeSuccess',
            function(event, toState, toParams, fromState, fromParams){
        if ($state.current.name === 'select_product_product') {
            // Set Focus
            angular.element(document.querySelector('#input_ean13'))[0].focus();
            $scope.data.ean13 = '';
            $scope.data.location_name = $rootScope.currentLocationName;
            $scope.data.parent_complete_name = $rootScope.currentLocationParentCompleteName;

            // Load current Stock Inventories
            StockInventoryModel.LoadInventory(
                    $rootScope.currentInventoryId).then(function (res){
                $scope.inventory = res;
            });
        }
    });

    $scope.submit = function () {
        if ($scope.data.ean13 in $rootScope.ProductListByEan13){
            $scope.errorMessage = "";
            $state.go('select_quantity', {ean13: $scope.data.ean13});
        }else{
            $scope.errorMessage = $translate.instant("Unknown EAN13 Barcode");
            angular.element(document.querySelector('#sound_user_error'))[0].play();
        }
    };

}]);
