
"use strict";
angular.module('mobile_app_inventory').factory(
    'SettingModel', [
    '$q', 'jsonRpc',
    function ($q, jsonRpc) {

    var setting_list = null;

    return {
        reset_list: function() {
            setting_list = null;
        },

        get_list: function() {
            setting_list = setting_list || jsonRpc.call(
                'mobile.app.inventory', 'get_settings', []);
            return setting_list;
        },

        get_setting: function(name) {
            return this.get_list().then(function (settings) {
                return settings[name];
            });
        },
    };
}]);
