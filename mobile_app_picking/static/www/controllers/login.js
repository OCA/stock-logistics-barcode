/* global angular */

'use strict'
angular.module('mobile_app_picking').controller(
  'LoginCtrl', [
    '$scope', 'jsonRpc', '$state', '$translate', 'tools',
    function ($scope, jsonRpc, $state, $translate, tools) {
      $scope.data = {
        'database': '',
        'databases': [],
        'login': '',
        'password': ''
      }

      $scope.$on('$ionicView.beforeEnter', function () {
        if ($state.current.name === 'logout') {
          jsonRpc.logout(true)
        }
      })

      $scope.init = function () {
        tools.focus()

        // Load available databases
        jsonRpc.getDbList().then(function (databases) {
          $scope.data.databases = databases
          if (databases.length >= 1) {
            $scope.data.database = databases[0]
          }
        }, function (reason) {
          $scope.errorMessage = $translate.instant('Unreachable Service')
        })
      }

      $scope.$on(
        '$stateChangeSuccess',
        function (event, toState, toParams, fromState, fromParams) {
          if ($state.current.name === 'login') {
            tools.focus()
          }
        })

      $scope.submit = function () {
        jsonRpc.login(
          $scope.data.database,
          $scope.data.login,
          $scope.data.password
        ).then(function (user) {
          jsonRpc.call(
            'mobile.app.picking',
            'check_group',
            ['stock.group_stock_user']
          ).then(function (res) {
            if (res) {
              $scope.errorMessage = ''
              $state.go('list_picking_type', {})
            } else {
              $scope.errorMessage = $translate.instant(
                'Insufficient Acces Right: you should be member of' +
                " 'Warehouse / user' group.")
            }
          })
        }, function (e) {
          $scope.errorMessage = $translate.instant('Bad Login / Password')
        })
      }
    }])
