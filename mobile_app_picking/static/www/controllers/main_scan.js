/* global angular */

'use strict'
angular.module('mobile_app_picking').controller(
  'MainScanCtrl', [
    '$scope', '$filter', '$state', '$translate', '$stateParams', 'MoveLineModel', 'tools',
    function ($scope, $filter, $state, $translate, $stateParams, MoveLineModel, tools) {
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

        // It's a barcode of a product
        if (tools.is_barcode(inputValue)) {
          MoveLineModel.get_by_barcode_product(
            $stateParams.picking_id,
            inputValue).then(function (moveLines) {
            if (moveLines.length === 0) {
              $scope.display_loading_end($translate.instant(
                'Barcode not found in the picking'))
            } else if (moveLines.length > 1) {
              $scope.display_loading_end($translate.instant(
                'Many operations found'))
            } else {
              // The exact line has been found
              moveLine = moveLines[0]
              var newQty = moveLine.qty_done + 1
              MoveLineModel.set_quantity(moveLine, newQty).then(function () {
                $scope.data.currentMoveLine = moveLine
                $scope.display_loading_end()
              })
            }
          })

        // It's a quantity
        } else if (tools.is_quantity_correct(inputValue)) {
          if (!$scope.data.currentMoveLine) {
            $scope.display_loading_end($translate.instant(
              'Please first scan a product'))
          } else {
            var moveLine = $scope.data.currentMoveLine
            MoveLineModel.set_quantity(moveLine, inputValue).then(function () {
              $scope.display_loading_end()
            })
          }

        // It's an error
        } else {
          $scope.display_loading_end($translate.instant('Incorrect quantity'))
        }
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
