'use strict';

angular.module('teleceptor.infocontroller', [])

.controller('infoController', ['$scope', '$http', 'infoService', '$compile', '$timeout', 'apiService', '$window', 'timeService', function($scope, $http, infoService, $compile, $timeout, apiService, $window, timeService){
    $scope.widgets = [];
    var StreamLoaded = false;
    var SensorLoaded = false;

    $scope.$watch(function(){
        SensorLoaded = false;
        return infoService.getSensorInfo();
    }, function(v){
        if(v === undefined) return;
        LoadSensor(v);
    });

    $scope.$watch(function(){
        StreamLoaded = false;
        return infoService.getStreamInfo();
    }, function(v){
        if(v === undefined) return;
        LoadStream(v);
    });

    function LoadSensor(v){
        if(v === undefined) return;
        if(SensorLoaded){
            updateInfo();
            return;
        }
        for(var i in $scope.widgets){
            if($scope.widgets[i].title === "Sensor Info"){
                $scope.widgets.splice(i);
            }
        }
        SensorLoaded = true;

        var newObj = {
            "title": "Sensor Info",
            "editing": false,
            "url": "sensors",
            "uuid": v.uuid
        };
        newObj.id = v.last_calibration.id;
        newObj.items = [
        [{
            "tabName": "Configuration",
            "name": "UUID",
            "value": v.uuid,
            "inputType": "text"
        },{
            "name": "Model",
            "value": v.model,
            "inputType": "text"
        },{
            "name": "Name",
            "value": v.name,
            "inputType": "text"
        },{
            "name": "Description",
            "value": v.description,
            "inputType": "text"
        },{
            "name": "Units",
            "value": v.units,
            "inputType": "text"
        },{
            "name": "Last Calibration",
            "value": v.last_calibration.timestamp,
            "inputType": "text"
        },{
            "name": "Calibration",
            "value": v.last_calibration.coefficients,
            "inputType": "input"
        }], [{
            "tabName": "ManualEntry",
            "name": "New Data",
            "value": "",
            "inputType": "input",
            "inputid": "manEntry"
        },{
            "name": "",
            "label": "Send",
            "inputType": "button",
            "btnId": "send_data"
        }], [{
            "tabName": "Export",
            "name": "Export",
            "label": "SQL",
            "inputType": "button",
            "btnId": "exportSqlBtn"
        }, {
            "name": "Export",
            "label": "Elastic Search",
            "inputType": "button",
            "btnId": "exportEsBtn"
        }]];

        var commandObj = [];
        if(v.sensor_IOtype){
            commandObj.push({
                "tabName": "Command",
                "name": "Command",
                "value": "enter commands",
                "inputType": "input",
                "inputid": "commandInput"
            });
            commandObj.push({
                "tabName": "Command",
                "name": "",
                "label": "Send",
                "inputType": "button",
                "btnId": "sendCommand"
            });
        } else {
            commandObj.push({
                "tabName": "Command",
                "name": v.uuid,
                "value": "Output Sensor",
                "inputType": "text"
            });
        }
        newObj.items.push(commandObj);

        var metaObj = [];

        for(var i in v.meta_data){
            metaObj.push({
                "tabName": "Metadata",
                "name": i,
                "value": v.meta_data[i],
                "inputType": "text"
            });
        }
        if(metaObj[0] === undefined){
            metaObj[0] = {
                "tabName": "Metadata",
                "name": "Metadata",
                "value": "No meta data exists.",
                "inputType": "text"
            };
        }
        newObj.items.push(metaObj);
        $scope.widgets.push(newObj);
        updateInfo();
    }

    function LoadStream(v){
        if(v === undefined) return;
        if(StreamLoaded){
            updateInfo();
            return;
        }
        StreamLoaded = true;
        for(var i in $scope.widgets){
            if($scope.widgets[i].title !== "Sensor Info"){
                $scope.widgets.splice(i);
            }
        }
        var newObj = {
            "title": "Stream Info",
            "editing": false,
            "url": "datastreams"
        };
        // newObj.id = v.last_calibration.id;
        newObj.id = v.id;
        newObj.items = [[{
            "name": "ID",
            "value": v.id,
            "inputType": "input"
        },{
            "name": "Name",
            "value": v.name,
            "inputType": "input"
        },{
            "name": "Description",
            "value": v.description,
            "inputType": "input"
        },{
            "name": "Minimum Value",
            "value": v.min_value,
            "inputType": "input"
        },{
            "name": "Maximum Value",
            "value": v.max_value,
            "inputType": "input"
        },{
            "name": "Sensor Name",
            "value": v.sensor,
            "inputType": "text"
        },{
            "name": "Paths",
            "value": v.paths,
            "inputType": "multiple"
        }]];

        $scope.widgets.push(newObj);
        updateInfo();
    }

    function updateInfo(){
        for(var i in $scope.widgets){
            if($scope.widgets[i].items.length > 1){
                var myDiv = angular.element("#tabs_"+$scope.widgets[i].url);
                if(myDiv.length === 0) return;
                var wrapper = "<ul class='nav nav-tabs'>";
                for(var j in $scope.widgets[i].items){
                    wrapper += "<li ";
                    if(j == 0) wrapper += "class='active'";
                    //make sure that the first item of each tab has the tabname property!
                    wrapper += "><a class='btn btn-link' id='"+ $scope.widgets[i].items[j][0].tabName +"_tab' ng-click='ChangeTab(" + j +")'>"+ $scope.widgets[i].items[j][0].tabName + "</a></li>";
                }
                wrapper += "</ul><br>";
                myDiv.html("");
                myDiv.append($compile(wrapper)($scope));
            }
        }
        for(var x in $scope.widgets){
            for(var y in $scope.widgets[x].items){
                var head = angular.element("#tabs_"+$scope.widgets[x].url);
                var body = angular.element("#"+$scope.widgets[x].items[y][0].tabName+"_body");
                if(y === "0"){
                    head.addClass("active");
                    body.css("display", "block");
                } else {
                    body.css("display", "none");
                    head.removeClass("active");
                }
            }
        }
    }

    $scope.currentTab = 0;
    $scope.ChangeTab = function(i){
        $scope.currentTab = i;
        $scope.widgets[1].editing = false;
        for(var x in $scope.widgets){
            for(var y in $scope.widgets[x].items){
                var head = angular.element("#"+$scope.widgets[x].items[y][0].tabName+"_tab");
                var body = angular.element("#"+$scope.widgets[x].items[y][0].tabName+"_body");
                if(head[0] === undefined) continue;
                if(parseInt(y) === parseInt(i)){
                    $(head[0].parentNode).addClass("active");
                    body.css("display", "block");
                } else {
                    body.css("display", "none");
                    $(head[0].parentNode).removeClass("active");
                }
            }
        }
    };

    $scope.AddPath = function(){
        for(var a in $scope.widgets){
            if($scope.widgets[a].url === "datastreams"){
                for(var b in $scope.widgets[a].items[0]){
                    if($scope.widgets[a].items[0][b].name === "Paths"){
                        $scope.widgets[a].items[0][b].value.push("/new_sensors_"+$scope.widgets[a].items[0][b].value.length);
                    }
                }
            }
        }
    };

    $scope.EditFields = function(template){
        for(var i in $scope.widgets){
            if($scope.widgets[i].title == template){
                $scope.widgets[i].editing = true;
            }
        }
    };

    $scope.SaveFields = function(template){
        var updates = {
            "type": template
        };
        var url = "";
        var cancel = false;
        for(var i in $scope.widgets){
            if($scope.widgets[i].url === template){
                url = $scope.widgets[i].url +"/";
                if($scope.widgets[i].url==="datastreams"){
                    url+= "?stream_id="+$scope.widgets[i].id;
                } else {
                    url+=  $scope.widgets[i].uuid;
                }

                for(var j in $scope.widgets[i].items[0]){
                    if($scope.widgets[i].items[0][j].inputType === "input"){
                        updates[$scope.widgets[i].items[0][j].name.toLowerCase()] = $("#"+template + "_" + j)[0].value.toLowerCase();
                    }
                    if($scope.widgets[i].items[0][j].inputType === "multiple"){
                        updates[$scope.widgets[i].items[0][j].name.toLowerCase()] = [];
                        for(var k in $scope.widgets[i].items[0][j].value){
                            var str = "#"+template + "_" + k + "_" + $scope.widgets[i].items[0][j].name;
                            var newPath =$(str)[0].value.toLowerCase();
                            if(newPath === ""){
                                continue;
                            }
                            if(newPath[0] != '/'){
                                ShowWarning(template, "Paths must begin with a '/'");
                                cancel = true;
                            }
                            if(newPath[newPath.length-1] == '/'){
                                ShowWarning(template, "Paths must not end with a '/'");
                                cancel = true;
                            }

                            var temp = newPath.split('/');
                            for(k in temp){
                                if(/[~`!#$%\^&*+=\-\[\]\\';,/{}|\\":<>\?]/g.test(temp[k])){
                                    ShowWarning(template, "Paths cannot have any special characters");
                                    cancel = true;
                                }
                            }
                            updates[$scope.widgets[i].items[0][j].name.toLowerCase()].push($(str)[0].value.toLowerCase());
                        }
                        if(updates[$scope.widgets[i].items[0][j].name.toLowerCase()].length === 0){
                            updates[$scope.widgets[i].items[0][j].name.toLowerCase()].push("/new_sensors");
                        }
                    }
                }

            }
        }
        if(cancel) return;
        if(updates.type == "sensors"){
            updates.last_calibration = {
                "coefficients": JSON.parse(updates.calibration)
            };
        }
        apiService.put(url, updates).then(function successCallback(response){
            $window.location.reload();
        }, function errorCallback(response){
            console.log("Error Occured: ", response.data);

        });
    };

    function ShowWarning(tag, msg){
        angular.element("#"+ tag+"_warning").html(msg).css('display', 'block');
    }

    $scope.CancelFields = function(template){
        for(var i in $scope.widgets){
            if($scope.widgets[i].title == template){
                $scope.widgets[i].editing = false;
            }
        }
    };
    $timeout(function(){
        angular.element('#exportEsBtn').on("click", function(){
            var start = timeService.getValues().start;
            var end = timeService.getValues().end;
            var readingsUrl = "readings?datastream=" + infoService.getStreamInfo().id + "&start="+parseInt(start/1000)+"&end="+parseInt(end/1000)+"&source=ElasticSearch";
            apiService.get(readingsUrl).then(function(readingsResponse){
                exportData(readingsResponse);
            });
        });
        angular.element('#exportSqlBtn').on("click", function(){
            exportData(null);
        });
        angular.element('#send_data').on("click", function(){
            var sensorInfo = infoService.getSensorInfo();
            var id = sensorInfo.uuid;
            var newValue = angular.element('#manEntry')[0].value;
            var time = (new Date()).getTime() / 1000;

            var sensorReading = {"name": id, "sensor_type": sensorInfo.sensor_type,
             "timestamp": time, "meta_data":{}};

            var payload = [{
                "info":{"uuid": "", "name":sensorInfo.name, "description": sensorInfo.description, "out": (sensorInfo.isInput ? [] : [sensorReading]),
                "in": (sensorInfo.isInput ? [sensorReading] : [])}, "readings": [[id, newValue, time]]
            }];

            apiService.post("station", payload).then(function(response){
                console.log(response);
            });
        });
        angular.element('#sendCommand').on("click", function(){
            sendCommand();
        });
    }, 1000);

    function exportData(readings){
            var time_start = timeService.getValues().start;
            var time_end = timeService.getValues().end;
            var sensorInfo = infoService.getSensorInfo();
            if(readings === null){
                readings = infoService.getReadingsInfo().readings;
            }

            var scaledReadings = [];
            for(var i = 0; i < readings.length; i++){
                scaledReadings.push(readings[i][1] * sensorInfo.last_calibration.coefficients[0] + sensorInfo.last_calibration.coefficients[1]);
            }

            // actual delimiter characters for CSV format
            var colDelim = ',';
            var rowDelim = '\r\n';

            //build csv string
            var csv = "";
            csv += "timestamp" + colDelim + "UUID" + colDelim + "value" + colDelim + "scaled value" + colDelim + "units" + rowDelim;
            for(var i=0; i < readings.length; i++){
                csv += readings[i][0] + colDelim + sensorInfo.uuid + colDelim + readings[i][1] + colDelim + scaledReadings[i] + colDelim + sensorInfo.units + rowDelim;
            }
            // Data URI
            var today = new Date();

            var downloadFilename = sensorInfo.uuid + "_" + today.getMonth() +1 + "-" + today.getDate() + "-" + today.getFullYear() + "_" + today.getHours() + ":" + today.getMinutes() + ".csv";
            //actually download
            var link = document.createElement("a");
            link.download = downloadFilename;
            link.href = 'data:application/csv;charset=utf-8,' + encodeURIComponent(csv);
            link.click();
    }

    function sendCommand(){
        var sensorInfo = infoService.getSensorInfo();
        //post new value to commands api
        var payload = {
            "message": angular.element('#commandInput')[0].value
           ,"duration": 60000,
           "sensor_id": sensorInfo.uuid
        };

        apiService.post("messages/", payload).then(function(response){
            console.log("the response was:");
            console.log(response);
        });

    }

}]);