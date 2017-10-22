"use strict";
angular.module('mobile_app_inventory').factory(
        'ResCompanyModel', [
        '$q', 'jsonRpc',
        function ($q, jsonRpc) {

    var setting_list = null;

    return {
        get_list: function(force) {
            if (force){
                setting_list = null;
            }
            setting_list = setting_list || jsonRpc.call(
                    'res.company', 'mobile_get_settings', []).then(function (res) {
                return res;
            });
            return setting_list;
        },

        get_setting: function(name) {
            return this.get_list(false).then(function (settings) {
                return settings[name];
            });
        },

    };
}]);
