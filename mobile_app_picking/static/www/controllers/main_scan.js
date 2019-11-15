/* global angular */

angular.module('mobile_app_picking').controller(
  'MainScanCtrl', [
    '$scope', '$filter', '$state', '$translate', '$stateParams', 'MoveModel',
    'tools',
    function ($scope, $filter, $state, $translate, $stateParams, MoveModel,
      tools) {
      $scope.data = {
        'inputData': null,
        'currentMove': null,
        'errorMessage': null,
      };

      $scope.$on(
        '$stateChangeSuccess',
        function (event, toState, toParams, fromState, fromParams) {
          if ($state.current.name === 'main_scan') {
            tools.focus();
            $scope.data.errorMessage = null;
            $scope.data.currentMove = null;
            $scope.data.inputData = null;
            if ($stateParams.move_id !== 0) {
              MoveModel.get_by_id(
                $stateParams.picking_id, $stateParams.move_id
              ).then(function (move) {
                if (move) {
                  $scope.data.currentMove = move;
                }
              });
            }
          }
        });

      $scope.submit = function () {
        $scope.display_loading_begin();
        var inputValue = $scope.data.inputData;

        // It's a barcode of a product
        if (tools.is_barcode(inputValue)) {
          MoveModel.get_by_barcode_product(
            $stateParams.picking_id,
            inputValue).then(function (moves) {
            if (moves.length === 0) {
              $scope.display_loading_end($translate.instant(
                'Barcode not found in the picking'));
            } else if (moves.length > 1) {
              $scope.display_loading_end($translate.instant(
                'Many operations found'));
            } else {
              // The exact move has been found
              move = moves[0];
              var newQty = move.qty_done + 1;
              MoveModel.set_quantity(move, newQty).then(function () {
                $scope.data.currentMove = move;
                $scope.display_loading_end();
              });
            }
          });

        // It's a quantity
        } else if (tools.is_quantity_correct(inputValue)) {
          if ($scope.data.currentMove) {
            var move = $scope.data.currentMove;
            MoveModel.set_quantity(move, inputValue).then(function () {
              $scope.display_loading_end();
            });
          } else {
            $scope.display_loading_end($translate.instant(
              'Please first scan a product'));
          }

        // It's an error
        } else {
          $scope.display_loading_end($translate.instant('Incorrect quantity'));
        }
      };

      $scope.display_loading_begin = function () {
        $scope.data.errorMessage = null;
        tools.display_loading_begin();
      };

      $scope.display_loading_end = function (errorMessage) {
        $scope.data.errorMessage = errorMessage;
        tools.display_loading_end();
        $scope.data.inputData = null;
      };
    }]);
