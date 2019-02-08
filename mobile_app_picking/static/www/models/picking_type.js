/* global angular */

'use strict'
angular.module('mobile_app_picking').factory(
  'PickingTypeModel', [
    '$q', 'jsonRpc',
    function ($q, jsonRpc) {
      return {
        get_list: function () {
          // always a fresh list
          return jsonRpc.call(
            'mobile.app.picking', 'get_picking_types', []).then(function (res) {
            return res
          })
        }

      }
    }])
