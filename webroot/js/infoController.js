'use strict';

angular.module('teleceptor.infocontroller', [])

.controller('infoController', ['$scope', '$http', 'infoService', '$compile', '$timeout', 'apiService', '$window', function($scope, $http, infoService, $compile, $timeout, apiService, $window){
    $scope.widgets = [];
    var StreamLoaded = false;
    var SensorLoaded = false;
    $scope.$watch(function(){
        return infoService.getSensorInfo();
    }, function(v){
        if(v === undefined) return;
        if(SensorLoaded){
            updateInfo();
            return;
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
            "tabName": "Metadata",
            "name": "Metadata",
            "value": v.meta_data,
            "inputType": "text"
        }], [{
            "tabName": "Command",
            "name": v.uuid,
            "value": "Output Sensor",
            "inputType": "text"

        }], [{
            "tabName": "ManualEntry",
            "name": "New Data",
            "value": "",
            "inputType": "input"
        },{
            "name": "",
            "label": "Send",
            "inputType": "button"
        }], [{
            "tabName": "Export",
            "name": "Export",
            "label": "SQL",
            "inputType": "button"
        }, {
            "name": "",
            "label": "Elastic Search",
            "inputType": "button"
        }]];
        $scope.widgets.push(newObj);
        updateInfo();
    });

    $scope.$watch(function(){
        return infoService.getStreamInfo();
    }, function(v){
        if(v === undefined) return;
        if(StreamLoaded){
            updateInfo();
            return;
        }
        StreamLoaded = true;
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
    });


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
                wrapper += "</ul>";
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
        if(i === 3)
            $scope.widgets[1].editing = true;
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
        apiService.set(url, updates).then(function successCallback(response){
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

}]);