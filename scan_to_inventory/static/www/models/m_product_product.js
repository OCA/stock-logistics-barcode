'use strict';


angular.module('scan_to_inventory').factory(
        'ProductProductModel', [
        '$q', '$rootScope', 'jsonRpc',
        function ($q, $rootScope, jsonRpc) {

    return {
        LoadProductList: function() {
            return jsonRpc.call(
                    'product.product', 'scan_to_inventory_load_product', []).then(function (res) {
                $rootScope.ProductListByEan13 = res;
                var quantity = 0;
                for (var a in res){quantity ++;}
                return quantity;
            });
        },

    };
}]);
