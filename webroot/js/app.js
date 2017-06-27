/*jslint node: true */
'use strict';

// Declare app level module which depends on views, and components
var app = angular.module('teleceptor', [ // jshint ignore:line
        'ngRoute',
        'teleceptor.timecontroller',
        'teleceptor.treecontroller',
        'teleceptor.graphcontroller',
        'teleceptor.streamcontroller',
        'teleceptor.sensorcontroller',
        'teleceptor.services',
        'teleceptor.maincontroller',
    ])

    .config(['$routeProvider', function($routeProvider) {
        $routeProvider.otherwise({
            redirectTo: '/',
        });
        $routeProvider.when('/', {
            templateUrl: 'base.html',
            reloadOnSearch: false,
        });
        $routeProvider.when('/generate_json', {
            templateUrl: 'generate_json.html',
            reloadOnSearch: false,
        });
    },
  ]);
