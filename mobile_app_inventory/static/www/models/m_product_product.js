"use strict";
angular.module('mobile_app_inventory').factory(
        'ProductProductModel', [
        '$q', '$rootScope', 'jsonRpc',
        function ($q, $rootScope, jsonRpc) {

    var products = {};

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
        get_product: function(ean13) {
            return $q(function (success, error) {
                if (products[ean13]) //search in cache
                    return success(products[ean13]);
                return jsonRpc.searchRead(
                    'product.product',
                    [['ean13','=', ean13]], ['name', 'ean13'],
                    {'limit': 1}
                ).then(function (res) {
                    if (res.length == 0)
                        return error('Product ' + ean13 + ' not found');
                    products[ean13] = res.records[0]; //set cache
                    return success(products[ean13]);
                });
            });
        }
    };
}]);
 
