angular.module('scan_to_inventory').factory(
        'StockLocationModel', [
        '$q', '$rootScope', 'jsonRpc',
        function ($q, $rootScope, jsonRpc) {

    return {
        LoadLocationList: function() {
            return jsonRpc.searchRead(
                    'stock.location', [['usage', '=', 'internal']], [
                    'id', 'name', 'parent_complete_name',
                    ]).then(function (res) {
                $rootScope.LocationList = res.records;
                return res.records.length;
            });
        },

    };
}]);
