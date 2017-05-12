/*jslint node: true */
'use strict';
var angular;
// Declare app level module which depends on views, and components
var app = angular.module('teleceptor', [
  'ngRoute',
  'teleceptor.timecontroller',
  'teleceptor.treecontroller',
  'teleceptor.graphcontroller',
  'teleceptor.infocontroller',
  'teleceptor.services',
  'teleceptor.maincontroller'
])

.config(['$routeProvider', '$locationProvider', '$httpProvider', function($routeProvider, $locationProvider, $httpProvider){
    $routeProvider.otherwise({redirectTo: '/'});
    $routeProvider.when('/', {
        templateUrl: 'base.html',
        reloadOnSearch: false
    });
}]);
