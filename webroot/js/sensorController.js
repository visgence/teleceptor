/*jslint node: true */
'use strict';

angular.module('teleceptor.sensorcontroller', ['frapontillo.bootstrap-switch'])

.controller('sensorController', ['$scope', '$http', 'infoService', '$compile', '$timeout', 'apiService', '$window', 'timeService', '$location', function($scope, $http, infoService, $compile, $timeout, apiService, $window, timeService, $location) {
    // tabs:
    // config, entry, export, command, metatdata
    $scope.tab = 'config';
    $scope.isSelected = 'yep'; //For the bootstrap switch in command.
    $scope.isActive = "false";


    $scope.$watch(function() {
        return infoService.getSensorInfo();
    }, function(v) {
        LoadSensor(v);
    });

    $scope.$on('$routeUpdate', function() {
        LoadSensor(infoService.getSensorInfo());
    });

    function LoadSensor(v) {
        if (v === undefined) return;
        for(var i in v){
            if(v[i] === null){
                v[i] = "-";
            }
        }
        $scope.sensor = v;

        if (v.sensor_type === "output") {
            $scope.isActive = true;
            //We need to set the preliminary state
        }        
    }

    $scope.ChangeTab = function(event, tab) {
        $scope.tab = tab;
        $('.nav-tabs li').removeClass('active');
        $(event.target.parentNode).toggleClass('active');
    };

    $scope.EditFields = function() {
        $scope.editing = true;
        $scope.previous_coefficients = $scope.sensor.last_calibration.coefficients;
    };

    $scope.CancelFields = function() {
        $scope.editing = false;
    };

    $scope.CommandSwitch = function(){

    };

    $scope.ExportEs = function(){
        var start = timeService.getValues().start;
        var end = timeService.getValues().end;
        var readingsUrl = "readings?datastream=" + infoService.getStreamInfo().id + "&start=" + parseInt(start / 1000) + "&end=" + parseInt(end / 1000) + "&source=ElasticSearch";
        apiService.get(readingsUrl).then(function(readingsResponse) {
            exportData(readingsResponse);
        });
    };

    $scope.ExportSQL = function(){
        exportData(null);
    };

    $scope.SaveFields = function() {
        var updateData = {};
        var url = "sensors";
        var editableFields = ['last_calibration', 'units', 'description', 'uuid'];
        
        for(var i in $scope.sensor){
            if(!(editableFields.includes(i))) continue;
            if($scope.sensor[i] === "-" || $scope.sensor[i] === ""){
                updateData[i] = null;
            } else {
                updateData[i] = $scope.sensor[i];
            }
        }
        if(updateData.last_calibration.coefficients !== $scope.previous_coefficients){
            updateData.last_calibration.timestamp = Date.now()/1000;
        }
        
        apiService.put(url, updateData).then(function successCallback(response) {
            $scope.editing = false;
            location.reload();
        }, function errorCallback(response) {
            console.log("Error Occured: ", response.data);

        });
    };

    function ShowWarning(tag, msg) {
        angular.element("#" + tag + "_warning").html(msg).css('display', 'block');
    }

    
    $timeout(function() {
        angular.element('#exportEsBtn').on("click", function() {
            var start = timeService.getValues().start;
            var end = timeService.getValues().end;
            var readingsUrl = "readings?datastream=" + infoService.getStreamInfo().id + "&start=" + parseInt(start / 1000) + "&end=" + parseInt(end / 1000) + "&source=ElasticSearch";
            apiService.get(readingsUrl).then(function(readingsResponse) {
                exportData(readingsResponse);
            });
        });
        angular.element('#exportSqlBtn').on("click", function() {
            exportData(null);
        });
        angular.element('#send_data').on("click", function() {
            var sensorInfo = infoService.getSensorInfo();
            var id = sensorInfo.uuid;
            var newValue = angular.element('#manEntry')[0].value;
            var time = (new Date()).getTime() / 1000;

            var sensorReading = {
                "name": id,
                "sensor_type": sensorInfo.sensor_type,
                "timestamp": time,
                "meta_data": {}
            };

            var payload = [{
                "info": {
                    "uuid": "",
                    "name": sensorInfo.name,
                    "description": sensorInfo.description,
                    "out": (sensorInfo.isInput ? [] : [sensorReading]),
                    "in": (sensorInfo.isInput ? [sensorReading] : [])
                },
                "readings": [
                    [id, newValue, time]
                ]
            }];

            apiService.post("station", payload).then(function(response) {
                console.log(response);
            });
        });
        angular.element('#sendCommand').on("click", function() {
            sendCommand();
        });
    }, 1000);

    function exportData(readings) {
        var time_start = timeService.getValues().start;
        var time_end = timeService.getValues().end;
        var sensorInfo = infoService.getSensorInfo();
        if (readings === null) {
            readings = infoService.getReadingsInfo().readings;
        }

        var scaledReadings = [];
        var i;
        for (i = 0; i < readings.length; i++) {
            scaledReadings.push(readings[i][1] * sensorInfo.last_calibration.coefficients[0] + sensorInfo.last_calibration.coefficients[1]);
        }

        // actual delimiter characters for CSV format
        var colDelim = ',';
        var rowDelim = '\r\n';

        //build csv string
        var csv = "";
        csv += "timestamp" + colDelim + "UUID" + colDelim + "value" + colDelim + "scaled value" + colDelim + "units" + rowDelim;
        for (i = 0; i < readings.length; i++) {
            csv += readings[i][0] + colDelim + sensorInfo.uuid + colDelim + readings[i][1] + colDelim + scaledReadings[i] + colDelim + sensorInfo.units + rowDelim;
        }
        // Data URI
        var today = new Date();

        var downloadFilename = sensorInfo.uuid + "_" + today.getMonth() + 1 + "-" + today.getDate() + "-" + today.getFullYear() + "_" + today.getHours() + ":" + today.getMinutes() + ".csv";
        //actually download
        var link = document.createElement("a");
        link.download = downloadFilename;
        link.href = 'data:application/csv;charset=utf-8,' + encodeURIComponent(csv);
        link.click();
    }

    function sendCommand() {
        var sensorInfo = infoService.getSensorInfo();
        //post new value to commands api
        var payload = {
            "message": angular.element('#commandInput')[0].value,
            "duration": 60000,
            "sensor_id": sensorInfo.uuid
        };
        apiService.post("messages/", payload).then(function(response) {
            console.log("the response was:");
            console.log(response);
        });
    }
}]);
