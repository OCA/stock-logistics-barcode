/* global angular */

angular.module('mobile_app_picking').factory(
  'tools', ['$state', function ($state) {
    return {

      focus: function () {
        setTimeout(function () {
          var items = angular.element(document.querySelector('.with_focus'));
          if (items.length) {
            items[0].focus();
          }
        });
      },

      display_loading_begin: function () {
        var items = angular.element(document.querySelector('.loading_item'));
        if (items.length) {
          items[0].classList.add('loading-active');
        }
      },

      display_loading_end: function () {
        var items = angular.element(document.querySelector('.loading_item'));
        if (items.length) {
          items[0].classList.remove('loading-active');
        }
      },

      is_barcode: function (input) {
        return (String(input)).length >= 8;
      },

      is_quantity_correct: function (input) {
        if (isNaN(parseFloat(input, 10))) {
          return false;
        } else if (parseFloat(input, 10) < 0) {
          return false;
        }
        return true;
      },

    };
  }]);
