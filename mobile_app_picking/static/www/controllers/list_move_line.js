/* global angular */

'use strict'
angular.module('mobile_app_picking').controller(
  'ListMoveLineCtrl', [
    '$scope', '$filter', '$state', '$stateParams', 'PickingModel', 'MoveLineModel', 'tools',
    function ($scope, $filter, $state, $stateParams, PickingModel, MoveLineModel, tools) {
      $scope.data = {
        'picking': null,
        'moveLines': [],
        'display_all': true,
        'filter': 'display'
      }

      $scope.$on(
        '$stateChangeSuccess',
        function (event, toState, toParams, fromState, fromParams) {
          if ($state.current.name === 'list_move_line') {
            tools.focus()
            MoveLineModel.get_list({ id: $stateParams.picking_id }).then(function (moveLines) {
              $scope.data.moveLines = moveLines
            })

            PickingModel.get_by_id(
              $stateParams.picking_type_id,
              $stateParams.picking_id
            ).then(function (picking) {
              $scope.data.picking = picking
            })
          }
        })

      $scope.click_display_all = function () {
        if ($scope.data.display_all === true) {
          $scope.data.filter = 'display'
        } else {
          $scope.data.filter = 'display_allways'
        }
      }

      $scope.reset_qty = function (moveLine) {
        MoveLineModel.set_quantity(moveLine, 0).then(function () {
          moveLine.qty_done = 0
        })
      }

      $scope.see_move_line = function (moveLine) {
        $state.go('main_scan', {
          picking_type_id: $stateParams.picking_type_id,
          picking_id: $stateParams.picking_id,
          move_line_id: moveLine.id
        })
      }
    }])
