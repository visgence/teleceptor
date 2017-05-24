/*jslint node: true */
'use strict';

angular.module('teleceptor.sensorcontroller', ['frapontillo.bootstrap-switch'])

.controller('sensorController', ['$scope', '$http', 'infoService', '$compile', '$timeout', 'apiService', '$window', 'timeService', function($scope, $http, infoService, $compile, $timeout, apiService, $window, timeService) {
    // tabs:
    // config, entry, export, command, metatdata
    $scope.tab = 'config'
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
        return
        updateInfo();
    }

    $scope.ChangeTab = function(event, tab) {
        $scope.tab = tab;
        $('.nav-tabs li').removeClass('active')
        $(event.target.parentNode).toggleClass('active')
    };

    $scope.EditFields = function() {
        $scope.editing = true;
    };

    $scope.CancelFields = function() {
        $scope.editing = false
    };

    $scope.CommandSwitch = function(){
    }






  

    










    function updateInfo() {
        var myDiv;
        for (var i in $scope.widgets) {
            if ($scope.widgets[i].items.length > 1) {
                myDiv = angular.element("#tabs_" + $scope.widgets[i].url);
                if (myDiv.length === 0) return;
                var wrapper = "<ul class='nav nav-tabs'>";
                for (var j in $scope.widgets[i].items) {
                    wrapper += "<li ";
                    if (j === 0) wrapper += "class='active'";
                    //make sure that the first item of each tab has the tabname property!
                    wrapper += "><a class='btn btn-link' id='" + $scope.widgets[i].items[j][0].tabName + "_tab' ng-click='ChangeTab(" + j + ")'>" + $scope.widgets[i].items[j][0].tabName + "</a></li>";
                }
                wrapper += "</ul><br>";
                myDiv.html("");
                myDiv.append($compile(wrapper)($scope));
            }
        }
        for (var x in $scope.widgets) {
            for (var y in $scope.widgets[x].items) {
                var head = angular.element("#tabs_" + $scope.widgets[x].url);
                var body = angular.element("#" + $scope.widgets[x].items[y][0].tabName + "_body");
                if (y === "0") {
                    head.addClass("active");
                    body.css("display", "block");
                } else {
                    body.css("display", "none");
                    head.removeClass("active");
                }
            }
        }
        if (myDiv !== undefined) {
            angular.element('#tabs_sensors').append(myDiv);
        }
    }

    



    $scope.SaveFields = function(template) {
        var updates = {
            "type": template
        };
        var url = "";
        var cancel = false;
        for (var i in $scope.widgets) {
            if ($scope.widgets[i].url === template) {
                url = $scope.widgets[i].url + "/";
                if ($scope.widgets[i].url === "datastreams") {
                    url += "?stream_id=" + $scope.widgets[i].id;
                } else {
                    url += $scope.widgets[i].uuid;
                }

                for (var j in $scope.widgets[i].items[0]) {
                    if ($scope.widgets[i].items[0][j].inputType === "input") {
                        updates[$scope.widgets[i].items[0][j].name.toLowerCase()] = $("#" + template + "_" + j)[0].value.toLowerCase();
                    }
                    if ($scope.widgets[i].items[0][j].inputType === "multiple") {
                        updates[$scope.widgets[i].items[0][j].name.toLowerCase()] = [];
                        for (var k in $scope.widgets[i].items[0][j].value) {
                            var str = "#" + template + "_" + k + "_" + $scope.widgets[i].items[0][j].name;
                            var newPath = $(str)[0].value.toLowerCase();
                            if (newPath === "") {
                                continue;
                            }
                            if (newPath[0] != '/') {
                                ShowWarning(template, "Paths must begin with a '/'");
                                cancel = true;
                            }
                            if (newPath[newPath.length - 1] == '/') {
                                ShowWarning(template, "Paths must not end with a '/'");
                                cancel = true;
                            }

                            var temp = newPath.split('/');
                            for (k in temp) {
                                if (/[~`!#$%\^&*+=\-\[\]\\';,/{}|\\":<>\?]/g.test(temp[k])) {
                                    ShowWarning(template, "Paths cannot have any special characters");
                                    cancel = true;
                                }
                            }
                            updates[$scope.widgets[i].items[0][j].name.toLowerCase()].push($(str)[0].value.toLowerCase());
                        }
                        if (updates[$scope.widgets[i].items[0][j].name.toLowerCase()].length === 0) {
                            updates[$scope.widgets[i].items[0][j].name.toLowerCase()].push("/new_sensors");
                        }
                    }
                }

            }
        }
        if (cancel) return;
        if (updates.type == "sensors") {
            updates.last_calibration = {
                "coefficients": JSON.parse(updates.calibration)
            };
        }
        apiService.put(url, updates).then(function successCallback(response) {
            $window.location.reload();
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
