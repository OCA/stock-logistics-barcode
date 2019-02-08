/* global angular */

'use strict'
angular.module('mobile_app_picking').controller(
  'MainScanCtrl', [
    '$scope', '$filter', '$state', '$stateParams', 'MoveLineModel', 'tools',
    function ($scope, $filter, $state, $stateParams, MoveLineModel, tools) {
      $scope.data = {
        'inputData': null,
        'currentMoveLine': null,
        'errorMessage': null
      }

      $scope.$on(
        '$stateChangeSuccess',
        function (event, toState, toParams, fromState, fromParams) {
          if ($state.current.name === 'main_scan') {
            tools.focus()
            $scope.data.errorMessage = null
            $scope.data.currentMoveLine = null
            $scope.data.inputData = null
            if ($stateParams.move_line_id !== 0) {
              MoveLineModel.get_by_id(
                $stateParams.picking_id, $stateParams.move_line_id
              ).then(function (moveLine) {
                if (moveLine) {
                  $scope.data.currentMoveLine = moveLine
                }
              })
            }
          }
        })

      $scope.submit = function () {
        $scope.display_loading_begin()
        var inputValue = $scope.data.inputData
        if (tools.is_barcode(inputValue)) {
          // It is a barcode of a product
          MoveLineModel.get_by_barcode_product(
            $stateParams.picking_id,
            inputValue).then(function (moveLine) {
            if (!moveLine) {
              $scope.display_loading_end('Unable to found the barcode ' + inputValue)
            } else {
              // The barcode has been found
              var newQty = moveLine.qty_done + 1
              MoveLineModel.set_quantity(moveLine, newQty).then(function () {
                $scope.data.currentMoveLine = moveLine
                $scope.display_loading_end()
              })
            }
          })
        } else if (!isNaN(parseFloat(inputValue, 10))) {
          // It is a quantity
          if (!$scope.data.currentMoveLine) {
            $scope.display_loading_end('Please scan a product before setting quantity')
          } else {
            var moveLine = $scope.data.currentMoveLine
            MoveLineModel.set_quantity(moveLine, inputValue).then(function () {
              $scope.display_loading_end()
            })
          }
        } else {
          $scope.display_loading_end('Incorrect value')
        }
      }

      $scope.go_to_move_line_list = function () {
        tools.focus()
        $state.go('move_line', {
          picking_type_id: $stateParams.picking_type_id,
          picking_id: $stateParams.picking_id
        })
      }

      $scope.display_loading_begin = function () {
        $scope.data.errorMessage = null
        tools.display_loading_begin()
      }

      $scope.display_loading_end = function (errorMessage) {
        $scope.data.errorMessage = errorMessage
        tools.display_loading_end()
        $scope.data.inputData = null
      }
    }])
