"use strict";
angular.module('mobile_app_inventory').factory(
        'ProductModel', [
        '$q', 'jsonRpc',
        function ($q, jsonRpc) {

    var product_promise = null;
    var products = {};
    var prod_inv = {};

    return {
        reset_list: function() {
            products = {};
        },

        get_list: function(inventory) {
            product_promise = product_promise || jsonRpc.call(
                'mobile.app.inventory', 'get_inventory_lines', 
                [{inventory: inventory}]).then(function (lines) {
                    lines.forEach(function(line) {
                        products[line.product.barcode] = line.product;
                        products[line.product.barcode].found = true;
                        //expected qty
                        if (!prod_inv[line.product.barcode])
                            prod_inv[line.product.barcode] = {};
                        prod_inv[line.product.barcode][line.location.id] = line.expected_qty;
                    });
                    return products;
            });
            return product_promise;
        },

        search_product: function(ean13) {
            return $q(function (success, error) {
                if (products[ean13]) {//search in cache
                    return success(products[ean13]);
                }
                jsonRpc.call('mobile.app.inventory', 'search_barcode', [{'barcode': ean13}]
                ).then(function (res) {
                    if (!res){
                        res = {'found': false, 'name': 'unkown', 'barcode': ean13, 'custom_vals': {}}; //error('Product ' + ean13 + ' not found');
                    } else {
                        res.found = true;
                    }
                    products[ean13] = res; //set cache
                    return success(products[ean13]);
                });
            });
        },

        get_product: function(id) {
            var found = false;
            Object.values(products).some(function (product) {
                if (product.id == id)
                    return found = product;
            });
            return found;
        }    
    };
}]);
 
