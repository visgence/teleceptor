'use strict';

angular.module('teleceptor.treecontroller', [])

.controller('treeController', ['$scope', '$location', '$http', '$compile', function($scope, $location, $http, $compile){
    $scope.pathSetSelection = $location.search().pathSet;
        if($scope.pathSetSelection === undefined){
            $scope.pathSetSelection = 0;
        }

        $scope.ChangePath = function(e){
            if(e == "next")
                e = $scope.pathSetSelection+1;
            if(e == "previous"){
                e = $scope.pathSetSelection-1;
            }
            $scope.pathSetSelection = e;
            $location.search('pathSet', e);

            RequestTree();
        };

        function GetTree(info){
            $scope.idData = info;
            if($scope.pathSetSelection > Object.keys(info.pathSets).length -1 ){
                $scope.pathSetSelection = 0;
                $location.search("pathSets", 0);
            }
            var data = [];
            var paths = {};
            var newUrl;
            var fullUrl = [];
            var i;
            for(var a in info.paths){
                if(typeof info.paths[a] === 'string'){
                    newUrl = info.paths[a].split("/");
                }else {
                    newUrl = info.paths[a].name.split("/");
                }

                fullUrl = [];
                for (i in newUrl){
                    fullUrl.push(newUrl[i]);
                }
                fullUrl.pop();
                if(info.paths[a].id === undefined){
                    fullUrl.push(newUrl[newUrl.length-1]);
                } else {
                    fullUrl.push(info.paths[a].id);
                }
                paths = CreatePathObj(paths, newUrl, fullUrl);
            }

            for(a in info.pathSets[$scope.pathSetSelection]){
                if(typeof info.pathSets[$scope.pathSetSelection][a] === 'string'){
                    newUrl = info.pathSets[$scope.pathSetSelection][a].split("/");
                } else {
                    newUrl = info.pathSets[$scope.pathSetSelection][a].name.split("/");
                }
                fullUrl = [];
                for (i in newUrl){
                    fullUrl.push(newUrl[i]);
                }
                paths = CreatePathObj(paths, newUrl, fullUrl, a);
            }
            var newTree = CreateNode(paths, newUrl);
            return newTree;
        }

        function CreatePathObj(paths, url, fullUrl, sensor=null){

            if(url === undefined || url.length === 0){
                return {"sensor": sensor, "fullUrl": fullUrl, "isEndPoint": true};
            }
            var newUrl = url.shift();
            if(!(newUrl in paths)){
                paths[newUrl] = {};
            }

            paths[newUrl] = CreatePathObj(paths[newUrl], url, fullUrl, sensor);
            return paths;
        }

        function CreateNode(paths, url){
            var arr = [];
            for(var i in paths){
                var newObj = {
                    "text": i,
                    "selectable": true,
                    "icon": "glyphicon glyphicon-stop",
                    "color": "#337ab7"
                };
                if(!("isEndPoint" in paths[i])){
                    newObj.nodes = CreateNode(paths[i]);
                } else {
                    newObj.key = paths[i].fullUrl;
                    newObj.sensor = paths[i].sensor
                }
                arr.push(newObj);
            }
            return arr;
        }

        function RequestTree(){
            var req = {
                method: 'POST',
                url: "/getPaths",
                headers: {
                    'Content-Type': undefined
                }
            };
            $http(req).then(function successCallback(response){
                // console.log(response);
                BuildPathSetWidget(response.data.pathSets);
                $('#myTree').treeview({data: GetTree(response.data)});
                $('#myTree').treeview('collapseAll', { silent: true });
                var curNode = $location.search().node;
                if(curNode !== undefined){
                    for(var i = 0; i <$scope.idData.paths.length+Object.keys($scope.idData.pathSets[$scope.pathSetSelection]).length; i++){
                        var node = $('#myTree').treeview('getNode', [i]);
                        if(node.sensor   == curNode){
                            $('#myTree').treeview('revealNode', [parseInt(node.nodeId)]);
                            $('#myTree').treeview('selectNode', [node.nodeId]);
                        }
                    }
                }
                $('#myTree').on('nodeSelected', function(event, data) {
                    // console.log(event, data)
                    if("nodes" in data) return;
                    $scope.$apply(function(){
                        $location.search('node', data.sensor);
                    });
                });
            }, function errorCallback(response){
                console.log("Error Occured: ", response.data);
            });
        }
        RequestTree();

        function BuildPathSetWidget(data){
            var val = Object.keys(data).length;
            if(val <= 1) return;
             var button = "<li><a href='#'></a></li>";
             var wrapper = "<nav aria-label='Page navigation'><ul class='pagination'>";
             var currentSet = $location.search().pathSet;
             if(currentSet === undefined) currentSet = 1;
             for(var i = 0; i < val; i++){
                if(i > 7){
                    //make arrows and break;
                    break;
                }
                var newButton = "<li><button class='btn btn-default";
                if(currentSet-1 === i) newButton += " active";
                newButton += "' ng-click=ChangePath(" + (i+1) + ")>" + (i+1) + "</button></li>";

                wrapper += newButton;
             }
             angular.element('#pathSetPaginator').html("");

            angular.element('#pathSetPaginator').append($compile(wrapper)($scope));
        }


}]);