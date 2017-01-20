'use strict';

angular.module('teleceptor.infocontroller', [])

.controller('infoController', ['$scope', '$http', 'infoService', '$compile', '$timeout', function($scope, $http, infoService, $compile, $timeout){
    $scope.widgets = [];
    var StreamLoaded = false;
    var SensorLoaded = false;
    $scope.$watch(function(){
        return infoService.getSensorInfo();
    }, function(v){

        console.log(v)
        if(v === undefined) return;
        if(StreamLoaded) return;
            var newObj = {
                "title": "Sensor Info",
                "editing": false,
                "url": "sensor"
            };
            newObj.id = v.last_calibration.id;
            newObj.items = [[{
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
            }],[
            //start new tab
            {
                "tabName": "Metadata",
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
            }

            ]];
        $scope.widgets.push(newObj);
    });

    $scope.$watch(function(){
        return infoService.getStreamInfo();
    }, function(v){
        if(v === undefined) return;
        if(StreamLoaded) return;
        var newObj = {
            "title": "Stream Info",
            "editing": false,
            "url": "stream"
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
    });


        $timeout(function(){
            for(var i in $scope.widgets){
                if($scope.widgets[i].items.length > 1){
                    var myDiv = angular.element("#tabs_"+$scope.widgets[i].url);
                    if(myDiv.length === 0) return;
                    var wrapper = "<ul class='nav nav-tabs'>";
                    for(var j in $scope.widgets[i].items){
                        wrapper += "<li ";
                        if(j == 0) wrapper += "class='active'";
                        //make sure that the first item of each tab has the tabname property!
                        wrapper += "><a class='btn btn-link' ng-click='ChangeTab(" + j +")'>"+ $scope.widgets[i].items[j][0].tabName + "</a></li>";
                    }
                    wrapper += "</ul>";
                    myDiv.html("");
                    myDiv.append($compile(wrapper)($scope));
                }
            }
            for(var x in $scope.widgets){
                for(var y in $scope.widgets[x].items){
                    var head = angular.element("#tabs_"+$scope.widgets[x].url);
                    var body = angular.element("#"+$scope.widgets[x].items[y][0].tabName);
                    if(y === "0"){
                        //select
                        head.addClass("active")
                    } else {
                        body.css("display", "none");
                        head.removeClass("active");
                    }
                }

            }
        });

    $scope.ChangeTab = function(i){
        console.log(i)
    };

    $scope.AddPath = function(){

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
        for(var i in $scope.widgets){
            if($scope.widgets[i].url === template){
                updates.url = $scope.widgets[i].url;
                updates.id = $scope.widgets[i].id;
                for(var j in $scope.widgets[i].items){
                    if($scope.widgets[i].items[j].inputType === "input"){
                        updates[$scope.widgets[i].items[j].name] = $("#"+template + "_" + j)[0].value;
                    }
                    if($scope.widgets[i].items[j].inputType === "multiple"){
                        updates[$scope.widgets[i].items[j].name] = [];
                        for(var k in $scope.widgets[i].items[j].value){
                            var str = "#"+template + "_" + k + "_" + $scope.widgets[i].items[j].name;
                            updates[$scope.widgets[i].items[j].name].push($(str)[0].value);
                        }
                    }
                }
            }
        }
        var myParams = {};
        var req = {
            method: 'POST',
            url: "/setData",
            params: updates,
            headers: {
                'Content-Type': "application/json"
            }
        };

         $http(req).then(function successCallback(response){
           //reload

        }, function errorCallback(response){
            console.log("Error Occured: ", response.data);
        });

    };

    $scope.CancelFields = function(template){
        for(var i in $scope.widgets){
            if($scope.widgets[i].title == template){
                $scope.widgets[i].editing = false;
            }
        }
    };

}]);