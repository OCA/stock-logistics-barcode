angular.module('mobile_app_inventory').factory(
        'ProductProductModel', [
        '$q', '$rootScope', 'jsonRpc',
        function ($q, $rootScope, jsonRpc) {

    return {
        LoadProductList: function() {
//            return jsonRpc.call(
//                    'product.product', 'mobile_app_inventory_load_product', []).then(function (res) {
             return jsonRpc.searchRead(
                     'product.product', [], ['name', 'ean13']).then(function (res) {
                $rootScope.ProductListByEan13 = res;
                var quantity = 0;
                return Object.keys(res).length;
            });
        },

    };
}]);
