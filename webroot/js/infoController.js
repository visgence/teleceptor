'use strict';

angular.module('teleceptor.infocontroller', [])

.controller('infoController', ['$scope', '$http', 'infoService', '$compile', '$timeout', function($scope, $http, infoService, $compile, $timeout){
    $scope.$watch(function(){
        return infoService.getInfo();
    }, function(v){
        if(v.length === 0) return;
        $scope.widgets = [];
        for(var i in v){
            var newObj = {
                "title": Object.keys(v[i])[0] + " info",
                "editing": false,
                "url": Object.keys(v[i])[0]
            };
            if(newObj.url === "sensor"){
                newObj.id = v[i].sensor.last_calibration.id;
                newObj.items = [[{
                    "tabName": "Configuration",
                    "name": "UUID",
                    "value": v[i].sensor.uuid,
                    "inputType": "text"
                },{
                    "name": "Model",
                    "value": v[i].sensor.model,
                    "inputType": "text"
                },{
                    "name": "Name",
                    "value": v[i].sensor.name,
                    "inputType": "text"
                },{
                    "name": "Description",
                    "value": v[i].sensor.description,
                    "inputType": "text"
                },{
                    "name": "Units",
                    "value": v[i].sensor.units,
                    "inputType": "text"
                },{
                    "name": "Last Calibration",
                    "value": v[i].sensor.last_calibration.timestamp,
                    "inputType": "text"
                },{
                    "name": "Calibration",
                    "value": v[i].sensor.last_calibration.coefficients,
                    "inputType": "input"
                }],[

                {
                    "tabName": "Metadata",
                    "name": "UUID",
                    "value": v[i].sensor.uuid,
                    "inputType": "text"
                },{
                    "name": "Model",
                    "value": v[i].sensor.model,
                    "inputType": "text"
                },{
                    "name": "Name",
                    "value": v[i].sensor.name,
                    "inputType": "text"
                },{
                    "name": "Description",
                    "value": v[i].sensor.description,
                    "inputType": "text"
                },{
                    "name": "Units",
                    "value": v[i].sensor.units,
                    "inputType": "text"
                },{
                    "name": "Last Calibration",
                    "value": v[i].sensor.last_calibration.timestamp,
                    "inputType": "text"
                },{
                    "name": "Calibration",
                    "value": v[i].sensor.last_calibration.coefficients,
                    "inputType": "input"
                }


                ]];
            }
            if(newObj.url === "stream"){
                newObj.id = v[i].stream.id;
                newObj.items = [[{
                    "name": "ID",
                    "value": v[i].stream.id,
                    "inputType": "input"
                },{
                    "name": "Name",
                    "value": v[i].stream.name,
                    "inputType": "input"
                },{
                    "name": "Paths",
                    "value": v[i].stream.paths,
                    "inputType": "multiple"
                },{
                    "name": "Sensor Name",
                    "value": v[i].stream.sensor,
                    "inputType": "text"
                }]];
            }
        $scope.widgets.push(newObj);
        }

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
                    // console.log(y)
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
    });

    $scope.ChangeTab = function(i){
        console.log(i)
    }

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

    $scope.DeleteFields = function(template){
        for(var i in $scope.widgets){
            if($scope.widgets[i].title == template){
                $scope.widgets[i].editing = true;
            }
        }
    };
}]);