
'use strict';

// Declare app level module which depends on views, and components
var app = angular.module('teleceptor', [
  'ngRoute',
  'teleceptor.timecontroller',
  'teleceptor.treecontroller',
  'teleceptor.graphcontroller',
  'teleceptor.infocontroller',
  'teleceptor.services'
])

.config(['$routeProvider', '$locationProvider', '$httpProvider', function($routeProvider, $locationProvider, $httpProvider){
    $routeProvider.otherwise({redirectTo: '/'});
    $routeProvider.when('/', {
        templateUrl: 'base.html',
        reloadOnSearch: false
    });
}]);
