/* global angular */

'use strict'
angular.module('mobile_app_picking').factory(
  'PickingModel', [
    '$q', 'jsonRpc',
    function ($q, jsonRpc) {
      function reset () {
        data.pickings = []
        data.promise = null
      }
      var data = {}
      reset()

      return {
        get_list: function (pickingType) {
          // get pickings for a given picking type
          // retrun a promise
          reset()

          data.promise = data.promise || jsonRpc.call(
            'mobile.app.picking', 'get_pickings', [{ 'picking_type': pickingType }]
          ).then(function (res) {
            data.pickings = res
            return res
          })
          return data.promise
        },

        get_by_id: function (pickingTypeId, pickingId) {
          return this.get_list({ 'id': pickingTypeId }).then(function (pickings) {
            var foundPicking = false
            pickings.forEach(function (picking) {
              if (picking.id === pickingId) {
                foundPicking = picking
              }
            })
            return foundPicking
          })
        },

        try_validate_picking: function (pickingId) {
          return jsonRpc.call(
            'mobile.app.picking', 'try_validate_picking', [{
              'picking': { 'id': pickingId } }]
          ).then(function (res) {
            return res
          })
        },

        confirm_picking: function (pickingId, action) {
          return jsonRpc.call(
            'mobile.app.picking', 'confirm_picking', [{
              'picking': { 'id': pickingId },
              'action': action }]
          ).then(function (res) {
            return res
          })
        }

      }
    }])
