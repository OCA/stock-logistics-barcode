/* global angular */

// Angular.module is a global place for creating, registering and retrieving
// Angular modules
// 'mobile_app_picking' is the name of this angular module example
// (also set in a <body> attribute in index.html)
// the 2nd parameter is an array of 'requires'
angular.module(
  'mobile_app_picking', [
    'ionic', 'ui.router', 'odoo', 'pascalprecht.translate'])

  .run(['jsonRpc', '$state', '$rootScope', function (
    jsonRpc, $state, $rootScope) {
    jsonRpc.errorInterceptors.push(function (a) {
      if (a.title === 'session_expired') {
        $state.go('login');
      }
    });
  }])

  .config([
    '$ionicConfigProvider', '$stateProvider', '$urlRouterProvider',
    '$translateProvider',
    function ($ionicConfigProvider, $stateProvider, $urlRouterProvider,
      $translateProvider) {
      $stateProvider
        .state(
          'login', {
            url: '/login',
            templateUrl: 'views/login.html',
            controller: 'LoginCtrl',
          })
        .state(
          'logout', {
            url: '/logout',
            templateUrl: 'views/login.html',
            controller: 'LoginCtrl',
          })
        .state(
          'credit', {
            url: '/credit',
            templateUrl: 'views/credit.html',
            controller: 'CreditCtrl',
          })
        .state(
          'list_picking_type', {
            url: '/list_picking_type',
            templateUrl: 'views/list_picking_type.html',
            controller: 'ListPickingTypeCtrl',
          })
        .state(
          'list_picking', {
            url: '/picking_type/{picking_type_id:int}/list_picking',
            templateUrl: 'views/list_picking.html',
            controller: 'ListPickingCtrl',
          })
        .state(
          'list_move', {
            url: '/picking_type/{picking_type_id:int}/picking/' +
            '{picking_id:int}/list_move',
            templateUrl: 'views/list_move.html',
            controller: 'ListMoveCtrl',
          })
        .state(
          'main_scan', {
            url: '/picking_type/{picking_type_id:int}/picking/' +
            '{picking_id:int}/main_scan/{move_id:int}',
            templateUrl: 'views/main_scan.html',
            controller: 'MainScanCtrl',
          })
        .state(
          'picking_validate', {
            url: '/picking_type/{picking_type_id:int}/picking/' +
            '{picking_id:int}/picking_validate/',
            templateUrl: 'views/picking_validate.html',
            controller: 'PickingValidateCtrl',
          });

      $ionicConfigProvider.views.transition('none');

      $urlRouterProvider.otherwise('/login');

      $translateProvider.useStaticFilesLoader({
        prefix: 'i18n/',
        suffix: '.json',
      }).registerAvailableLanguageKeys(['en', 'fr'], {
        'en': 'en',
        'en_GB': 'en',
        'en_US': 'en',
        'fr': 'fr',
      })
        .preferredLanguage('en')
        .fallbackLanguage('en')
        .determinePreferredLanguage()
        .useSanitizeValueStrategy('escapeParameters');
    }])
  .controller('AppCtrl', [
    '$scope', '$state', '$stateParams', '$rootScope',
    function ($scope, $state, $stateParams, $rootScope) {
      $rootScope.$on('$stateChangeError', console.log.bind(console));
      $scope.$on('$stateChangeSuccess',
        function (evt, toState, toParams, fromState, fromParams) {
          // For side menu
          $rootScope.currentState = toState.name;
          $rootScope.params = toParams;
        }
      );
    },
  ]);
