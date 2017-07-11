/*jslint node: true */
'use strict';

angular.module('teleceptor.streamcontroller', [])

    .controller('streamController', ['$scope', 'infoService', 'apiService', function($scope, infoService, apiService) {

        $scope.stream = {};
        $scope.editing = false;
        $scope.ShowInfo = false;

        function LoadStream(v) {
            if (v === undefined) return;
            var dataToDisplay = {};
            for (var i in v) {
                if (v[i] === null) {
                    dataToDisplay[i] = "-";
                } else if (i === 'paths') {
                    dataToDisplay.paths = [];
                    for (var j in v[i]) {
                        dataToDisplay.paths.push({
                            url: v[i][j],
                        });
                    }
                } else {
                    dataToDisplay[i] = v[i];
                }
            }
            $scope.stream = dataToDisplay;
            $scope.ShowInfo = true;
            return;
        }

        $scope.$watch(function() {
            return infoService.getStreamInfo();
        }, function(v) {
            LoadStream(v);
        });

        $scope.$on('$routeUpdate', function() {
            LoadStream(infoService.getStreamInfo());
        });

        $scope.EditFields = function() {
            $('#warning-message').css('display', 'none');
            $scope.editing = true;
        };

        $scope.CancelFields = function() {
            $scope.editing = false;
        };

        $scope.AddPath = function() {
            $scope.stream.paths.push({
                url: "/new_path_" + $scope.stream.paths.length,
            });
        };

        $scope.SaveFields = function() {


            var updateData = {};
            var hasErrors = false;
            for (var i in $scope.stream) {
                if ($scope.stream[i] === "-" || $scope.stream[i] === "") {
                    updateData[i] = null;
                } else if (i === 'paths') {
                    updateData.paths = [];
                    for (var j in $scope.stream[i]) {
                        if ($scope.stream[i][j].url === "") continue;
                        if (!$scope.stream[i][j].url.startsWith('/')) {
                            $('#warning-message').css('display', 'block');
                            $('#warning-message').html('Paths must begin with a "/".');
                            hasErrors = true;
                            continue;
                        }
                        if ($scope.stream[i][j].url.includes(' ')) {
                            $('#warning-message').css('display', 'block');
                            $('#warning-message').html('Paths cannot have any spaces.');
                            hasErrors = true;
                            continue;
                        }
                        updateData.paths[j] = $scope.stream[i][j].url;
                    }
                } else {
                    updateData[i] = $scope.stream[i];
                }
            }
            if (hasErrors) {
                return;
            }
            var url = "datastreams/" + updateData.id;
            apiService.put(url, updateData).then(function successCallback() {
                $scope.editing = false;
                location.reload();
            }, function errorCallback(response) {
                console.log("Error Occured: ", response.data);
            });
        };
    },
  ]);
