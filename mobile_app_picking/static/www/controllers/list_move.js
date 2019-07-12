/* global angular */

angular.module('mobile_app_picking').controller(
  'ListMoveCtrl', [
    '$scope', '$filter', '$state', '$stateParams', 'PickingModel', 'MoveModel',
    'tools',
    function ($scope, $filter, $state, $stateParams, PickingModel, MoveModel,
      tools) {
      $scope.data = {
        'picking': null,
        'moves': [],
        'display_all': true,
        'filter': 'display',
      };

      $scope.$on(
        '$stateChangeSuccess',
        function (event, toState, toParams, fromState, fromParams) {
          if ($state.current.name === 'list_move') {
            tools.focus();
            MoveModel.get_list({id: $stateParams.picking_id})
              .then(function (moves) {
                $scope.data.moves = moves;
              });

            PickingModel.get_by_id(
              $stateParams.picking_type_id,
              $stateParams.picking_id
            ).then(function (picking) {
              $scope.data.picking = picking;
            });
          }
        });

      $scope.click_display_all = function () {
        if ($scope.data.display_all === true) {
          $scope.data.filter = 'display';
        } else {
          $scope.data.filter = 'display_allways';
        }
      };

      $scope.reset_qty = function (move) {
        MoveModel.set_quantity(move, 0).then(function () {
          move.qty_done = 0;
        });
      };

      $scope.see_move = function (move) {
        $state.go('main_scan', {
          picking_type_id: $stateParams.picking_type_id,
          picking_id: $stateParams.picking_id,
          move_id: move.id,
        });
      };
    }]);
