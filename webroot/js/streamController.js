/*jslint node: true */
'use strict';

angular.module('teleceptor.streamcontroller', [])

.controller('streamController', ['$scope', '$http', 'infoService', '$compile', '$timeout', 'apiService', '$window', 'timeService', function($scope, $http, infoService, $compile, $timeout, apiService, $window, timeService) {

    $scope.stream = {};
    $scope.editing = false;

    $scope.$watch(function() {
        return infoService.getStreamInfo();
    }, function(v) {
        LoadStream(v);
    });

    $scope.$on('$routeUpdate', function() {
        LoadStream(infoService.getStreamInfo());
    });

    function LoadStream(v) {
        if (v === undefined) return;
        for(var i in v){
            if(v[i] === null){
                v[i] = "-";
            }
        }
        $scope.stream = v;
        return
    }

    $scope.EditFields = function() {
        $scope.editing = true;
    };
        
    $scope.CancelFields = function() {
        $scope.editing = false
    };

    $scope.AddPath = function() {
        $scope.stream.paths[Object.keys($scope.stream.paths).length] = "/new_path_" + Object.keys($scope.stream.paths).length
    };

    $scope.SaveFields = function() {
        var updates = {

        };

        //     if ($scope.widgets[i].url === template) {
        //         url = $scope.widgets[i].url + "/";
        //         if ($scope.widgets[i].url === "datastreams") {
        //             url += "?stream_id=" + $scope.widgets[i].id;
        //         } else {
        //             url += $scope.widgets[i].uuid;
        //         }

        //         for (var j in $scope.widgets[i].items[0]) {
        //             if ($scope.widgets[i].items[0][j].inputType === "input") {
        //                 updates[$scope.widgets[i].items[0][j].name.toLowerCase()] = $("#" + template + "_" + j)[0].value.toLowerCase();
        //             }
        //             if ($scope.widgets[i].items[0][j].inputType === "multiple") {
        //                 updates[$scope.widgets[i].items[0][j].name.toLowerCase()] = [];
        //                 for (var k in $scope.widgets[i].items[0][j].value) {
        //                     var str = "#" + template + "_" + k + "_" + $scope.widgets[i].items[0][j].name;
        //                     var newPath = $(str)[0].value.toLowerCase();
        //                     if (newPath === "") {
        //                         continue;
        //                     }
        //                     if (newPath[0] != '/') {
        //                         ShowWarning(template, "Paths must begin with a '/'");
        //                         return;
        //                     }
        //                     if (newPath[newPath.length - 1] == '/') {
        //                         ShowWarning(template, "Paths must not end with a '/'");
        //                         return;
        //                     }

        //                     var temp = newPath.split('/');
        //                     for (k in temp) {
        //                         if (/[~`!#$%\^&*+=\-\[\]\\';,/{}|\\":<>\?]/g.test(temp[k])) {
        //                             ShowWarning(template, "Paths cannot have any special characters");
        //                             return;
        //                         }
        //                     }
        //                     updates[$scope.widgets[i].items[0][j].name.toLowerCase()].push($(str)[0].value.toLowerCase());
        //                 }
        //                 if (updates[$scope.widgets[i].items[0][j].name.toLowerCase()].length === 0) {
        //                     updates[$scope.widgets[i].items[0][j].name.toLowerCase()].push("/new_sensors");
        //                 }
        //             }
        //         }

        //     }
        // // }
        // if (cancel) return;
        // if (updates.type == "sensors") {
        //     updates.last_calibration = {
        //         "coefficients": JSON.parse(updates.calibration)
        //     };
        // }
        // apiService.put(url, updates).then(function successCallback(response) {
        //     $window.location.reload();
        // }, function errorCallback(response) {
        //     console.log("Error Occured: ", response.data);

        // });
    };

    function ShowWarning(tag, msg) {
        angular.element("#" + tag + "_warning").html(msg).css('display', 'block');
    }
}]);
