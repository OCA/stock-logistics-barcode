/* global angular */

angular.module('mobile_app_picking').controller(
  'ListPickingCtrl', [
    '$scope', '$filter', '$state', '$stateParams', 'PickingModel', 'tools',
    function ($scope, $filter, $state, $stateParams, PickingModel, tools) {
      $scope.data = {
        'pickings': [],
        'filter': null,
      };

      $scope.$on(
        '$stateChangeSuccess',
        function (event, toState, toParams, fromState, fromParams) {
          if ($state.current.name === 'list_picking') {
            tools.focus();
            $scope.data.filter = null;
            PickingModel.get_list({id: $stateParams.picking_type_id})
              .then(function (pickings) {
                $scope.data.pickings = pickings;
              });
          }
        });
    }]);
