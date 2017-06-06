/*jslint node: true */
'use strict';

angular.module('teleceptor.maincontroller', [])


.controller('mainController', ['$scope', 'apiService', function($scope, apiService) {
    $scope.mainPage = true;

    apiService.get('sysdata').then(function(response){
        $scope.versionNumber = response.data.version;
    });
}]);

