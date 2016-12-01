angular.module('scan_to_inventory').controller(
        'SelectStockInventoryCtrl', [
        '$scope', '$rootScope', 'jsonRpc', '$state', 'StockInventoryModel', '$translate',
        function ($scope, $rootScope, jsonRpc, $state, StockInventoryModel, $translate) {

    $scope.data = {
        'inventory_qty': 0,
        'inventory_list': false,
    };

    $scope.$on(
            '$stateChangeSuccess',
            function(event, toState, toParams, fromState, fromParams){
        if ($state.current.name === 'select_stock_inventory') {
            $scope.data.inventory_name = '';
            $scope.data.inventory_list = $rootScope.DraftInventoryList;
            $scope.data.inventory_qty = $rootScope.DraftInventoryList.length;
        }
    });

    $scope.selectInventory = function (id) {
        $rootScope.currentInventoryId = id;
        $state.go('select_stock_location');
    };

    $scope.submit = function () {
        if ($scope.data.inventory_name !== '') {
            StockInventoryModel.CreateInventory($scope.data.inventory_name).then(function(inventory_id){
                $rootScope.currentInventoryId = inventory_id;
                $state.go('select_stock_location');
            });
        }else{
            $scope.errorMessage = $translate.instant("Inventory Name Required");
        }
    };

}]);
