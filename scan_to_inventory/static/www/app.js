// Ionic Starter App

// angular.module is a global place for creating, registering and retrieving Angular modules
// 'scan_to_purchase' is the name of this angular module example (also set in a <body> attribute in index.html)
// the 2nd parameter is an array of 'requires'
angular.module(
        'scan_to_inventory', [
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

    $stateProvider.state(
        'login', {
            url: '/login',
            templateUrl: 'views/v_login.html',
            controller: 'LoginCtrl'
    }).state(
        'logout', {
            url: '/logout',
            templateUrl: 'views/v_login.html',
            controller: 'LoginCtrl'
    }).state(
        'credit', {
            url: '/credit',
            templateUrl: 'views/v_credit.html',
            controller: 'CreditCtrl'
    }).state(
        'load', {
            url: '/load',
            templateUrl: 'views/v_load.html',
            controller: 'LoadCtrl'
    }).state(
        'select_stock_inventory', {
            url: '/select_stock_inventory',
            templateUrl: 'views/v_select_stock_inventory.html',
            controller: 'SelectStockInventoryCtrl'
    }).state(
        'select_stock_location', {
            url: '/select_stock_location',
            templateUrl: 'views/v_select_stock_location.html',
            controller: 'SelectStockLocationCtrl'
    }).state(
        'select_product_product', {
            url: '/select_product_product',
            templateUrl: 'views/v_select_product_product.html',
            controller: 'SelectProductProductCtrl'
    }).state(
        'select_quantity', {
            url: '/select_quantity/:ean13',
            templateUrl: 'views/v_select_quantity.html',
            controller: 'SelectQuantityCtrl'
    }).state(
        'confirm_quantity', {
            url: '/confirm_quantity/:product_id:current_qty:new_qty',
            templateUrl: 'views/v_confirm_quantity.html',
            controller: 'ConfirmQuantityCtrl'
    });

    $urlRouterProvider.otherwise('login');

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
    '$scope', '$state', '$rootScope',
    function($scope, $state, $rootScope) {
        $scope.$on(
            '$stateChangeSuccess',
            function(evt, toState, toParams, fromState, fromParams) {
                $rootScope.currentState = toState.name;
            }
        );
    }
])

;
