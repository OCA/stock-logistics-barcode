/* global angular */

'use strict'
angular.module('mobile_app_picking').factory(
  'MoveLineModel', [
    '$q', 'jsonRpc',
    function ($q, jsonRpc) {
      function reset () {
        data.picking = null
        data.moveLines = []
        data.promise = null
      }
      var data = {}
      reset()

      return {
        get_list: function (picking) {
          // get move lines for a given picking
          // return a promise
          var self = this
          if (data.picking && data.promise && data.picking.id === picking.id) {
            // return cached data if available
            return data.promise
          }
          reset()

          data.promise = data.promise || jsonRpc.call(
            'mobile.app.picking', 'get_move_lines', [{ 'picking': picking }]
          ).then(function (moveLines) {
            data.picking = picking
            moveLines.forEach(function (moveLine) {
              self.compute_state(moveLine)
            })
            data.moveLines = moveLines
            return data.moveLines
          })
          return data.promise
        },

        compute_state: function (moveLine) {
          if (moveLine.qty_done === 0) {
            moveLine.state = 'unset'
          } else if (moveLine.qty_done < moveLine.qty_expected) {
            moveLine.state = 'pending'
          } else if (moveLine.qty_done === moveLine.qty_expected) {
            moveLine.state = 'done'
          } else {
            moveLine.state = 'too_much'
          }
        },

        get_by_id: function (pickingId, moveLineId) {
          return this.get_list({ 'id': pickingId }).then(function (moveLines) {
            var foundMoveLine = false
            moveLines.forEach(function (moveLine) {
              if (moveLine.id === moveLineId) {
                foundMoveLine = moveLine
              }
            })
            return foundMoveLine
          })
        },

        get_by_barcode_product: function (pickingId, barcode) {
          return this.get_list({ 'id': pickingId }).then(function (moveLines) {
            var foundMoveLine = false
            moveLines.forEach(function (moveLine) {
              if (moveLine.product.barcode === barcode.toString()) {
                foundMoveLine = moveLine
              }
            })
            return foundMoveLine
          })
        },

        set_quantity: function (moveLine, qtyDone) {
          var self = this
          qtyDone = parseFloat(qtyDone, 10)
          return jsonRpc.call(
            'mobile.app.picking', 'set_quantity', [{ 'move_line': moveLine, 'qty_done': qtyDone }]
          ).then(function (res) {
            moveLine.qty_done = qtyDone
            self.compute_state(moveLine)
            return res
          })
        }

      }
    }])
