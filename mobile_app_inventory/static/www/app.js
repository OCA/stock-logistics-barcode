"use strict";
// angular.module is a global place for creating, registering and retrieving Angular modules
// 'mobile_app_inventory' is the name of this angular module example (also set in a <body> attribute in index.html)
// the 2nd parameter is an array of 'requires'
angular.module(
        'mobile_app_inventory', [
        'ionic', 'ui.router', 'odoo', 'pascalprecht.translate'])

.run(function($ionicPlatform) {
    $ionicPlatform.ready(function() {
        // Hide the accessory bar by default (remove this to show the 
        //accessory bar above the keyboard for form inputs)
        if(window.StatusBar) {
            StatusBar.styleDefault();
        }
    });
})
.run(['jsonRpc', '$state', '$rootScope', function (jsonRpc, $state, $rootScope) {
    jsonRpc.errorInterceptors.push(function (a) {
        if (a.title === 'session_expired')
            $state.go('login');
    });
    $rootScope.logout = function() {
        $state.go('logout');
    };
}])
.config([
        '$ionicConfigProvider', '$stateProvider', '$urlRouterProvider', '$translateProvider',
        function ($ionicConfigProvider, $stateProvider, $urlRouterProvider, $translateProvider) {

    $stateProvider
    .state(
        'login', {
            url: '/login',
            templateUrl: 'views/login.html',
            controller: 'LoginCtrl'
    }).state(
        'logout', {
            url: '/logout',
            templateUrl: 'views/login.html',
            controller: 'LoginCtrl'
    }).state(
        'credit', {
            url: '/credit',
            templateUrl: 'views/credit.html',
            controller: 'CreditCtrl'
    }).state(
        'inventory', {
            url: '/inventory/',
            templateUrl: 'views/inventory.html',
            controller: 'InventoryCtrl'
    }).state(
        'location', {
            url: '/inventory/{inventory_id:int}/',
            templateUrl: 'views/location.html',
            controller: 'LocationCtrl'
    }).state(
        'select_location', {
            url: '/inventory/:inventory_name/location',
            templateUrl: 'views/location.html',
            controller: 'LocationCtrl'
    }).state(
        'product', {
            url: '/inventory/{inventory_id:int}/location/{location_id:int}/',
            templateUrl: 'views/main_scan.html',
            controller: 'MainScanCtrl'
    }).state(
        'confirm_quantity', {
            url: '/inventory/{inventory_id:int}/location/{location_id:int}/product/:product_id/confirm_quantity/:current_qty/:new_qty',
            templateUrl: 'views/confirm_quantity.html',
            controller: 'ConfirmQuantityCtrl'
    });

    $ionicConfigProvider.views.transition('none');

    $urlRouterProvider.otherwise('/inventory/');

    $translateProvider.useStaticFilesLoader({
            prefix: 'i18n/',
            suffix: '.json'
        }).registerAvailableLanguageKeys(['en', 'fr'], {
            'en' : 'en', 'en_GB': 'en', 'en_US': 'en',
            'fr' : 'fr',
        })
        .preferredLanguage('en')
        .fallbackLanguage('en')
        .determinePreferredLanguage()
        .useSanitizeValueStrategy('escapeParameters');

}])
.controller('AppCtrl', [
    '$scope', '$state', '$stateParams', '$rootScope',
    function($scope, $state, $stateParams, $rootScope) {
        $rootScope.$on("$stateChangeError", console.log.bind(console));
        $scope.$on('$stateChangeSuccess',
            function(evt, toState, toParams, fromState, fromParams) {
                //for side menu
                $rootScope.currentState = toState.name;
                $rootScope.params = toParams;
            }
        );
    }
])

;
