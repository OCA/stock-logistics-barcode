/* global angular */

angular.module('mobile_app_picking').factory(
  'MoveModel', [
    '$q', 'jsonRpc',
    function ($q, jsonRpc) {
      function reset () {
        data.picking = null;
        data.moves = [];
        data.promise = null;
      }
      var data = {};
      reset();

      return {
        get_list: function (picking) {
          // Get moves for a given picking
          // return a promise
          var self = this;
          if (data.picking && data.promise && data.picking.id === picking.id) {
            // Return cached data if available
            return data.promise;
          }
          reset();

          data.promise = data.promise || jsonRpc.call(
            'mobile.app.picking', 'get_moves', [{'picking': picking}]
          ).then(function (moves) {
            data.picking = picking;
            moves.forEach(function (move) {
              self.compute_state(move);
            });
            data.moves = moves;
            return data.moves;
          });
          return data.promise;
        },

        compute_state: function (move) {
          if (move.qty_done === 0) {
            move.state = 'unset';
            move.display_state = 'display_allways';
          } else if (move.qty_done < move.qty_expected) {
            move.state = 'pending';
            move.display_state = 'display_allways';
          } else if (move.qty_done === move.qty_expected) {
            move.state = 'done';
            move.display_state = 'display';
          } else {
            move.state = 'too_much';
            move.display_state = 'display_allways';
          }
        },

        get_by_id: function (pickingId, moveId) {
          return this.get_list({'id': pickingId}).then(function (moves) {
            var foundMove = false;
            moves.forEach(function (move) {
              if (move.id === moveId) {
                foundMove = move;
              }
            });
            return foundMove;
          });
        },

        get_by_barcode_product: function (pickingId, barcode) {
          return this.get_list({'id': pickingId}).then(function (moves) {
            var foundMoves = [];
            moves.forEach(function (move) {
              if (move.product.barcode === barcode.toString()) {
                foundMoves.push(move);
              }
            });
            return foundMoves;
          });
        },

        set_quantity: function (move, qtyDone) {
          var self = this;
          var qtyDoneFloat = parseFloat(qtyDone, 10);
          return jsonRpc.call(
            'mobile.app.picking', 'set_quantity',
            [{'move': move, 'qty_done': qtyDoneFloat}]
          ).then(function (res) {
            move.qty_done = qtyDoneFloat;
            self.compute_state(move);
            return res;
          });
        },

      };
    }]);
