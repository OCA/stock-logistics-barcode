"use strict";
angular.module('mobile_app_inventory').factory(
        'ProductProductModel', [
        '$q', 'jsonRpc',
        function ($q, jsonRpc) {

    var product_list = null;

    return {
        get_list: function(force, inventory_id) {
            if (force){
                product_list = null;
            }
            product_list = product_list || jsonRpc.call(
                    'product.product', 'mobile_inventory_load_products', [inventory_id]).then(function (res) {
                    console.log("ProductProductModel::get_list::success");
                return res;
            });
            return product_list;
        },

        get_product: function(ean13) {
            return this.get_list(false, false).then(function (products) {
                //Search In the Cache
                if (products[ean13] !== undefined){
                    console.log("trouvé in cache");
                    // products has been found in cache
                    return products[ean13];
                }
                // Call BackOffice
                
                // Return Error
                console.log("PAS TROUVE");
//                var found = false;
//                locations.some(function(location) {
//                    if (location.id != id)
//                        return false;
//                    found = location;
//                    return;
//                });
//                return found || $q.reject('Location not found');
            });
        },


//        get_product: function(ean13) {
//            console.log("get_product", ean13);
//            return $q(function (success, error) {
//                if (product_list[ean13]) //search in cache
//                    console.log("In CACHE");
//                    return success(product_list[ean13]);
////                return jsonRpc.searchRead(
////                    'product.product',
////                    [['ean13','=', ean13]], ['name', 'ean13'],
////                    {'limit': 1}
////                ).then(function (res) {
////                    if (res.length == 0)
////                        return error('Product ' + ean13 + ' not found');
////                    product_list[ean13] = res.records[0]; //set cache
////                    return success(product_list[ean13]);
////                });
//            });
//        },
    };
}]);
 
