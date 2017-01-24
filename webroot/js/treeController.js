'use strict';

angular.module('teleceptor.treecontroller', [])

.controller('treeController', ['$scope', '$location', '$http', '$compile', 'apiService', 'infoService', '$timeout', function($scope, $location, $http, $compile, apiService, infoService, $timeout){
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

        function MakeTreeStructure(data, stream, curUrl, pathId){
            if(curUrl.length === 1){
                if(!(curUrl[0] in data)) data[curUrl[0]] = [];
                stream.pathId = pathId;
                data[curUrl[0]].push(stream);
                return data;
            }
            if(!(curUrl[0] in data)) data[curUrl[0]] = {};
            var temp = curUrl.shift();
            data[temp] =  MakeTreeStructure(data[temp], stream, curUrl, pathId);
            return data;
        }

        function RequestTree(){
            var pathSetId = $location.search().pathSet-1;
            if(pathSetId === undefined) pathSetId = 0;
            apiService.get('datastreams').then(function(response){
                var streams = response.data.datastreams;
                var data = {};

                for(var a in streams){
                    for(var b in streams[a].paths){
                        if(parseInt(b) !== pathSetId) continue;
                        var curUrl = streams[a].paths[b].split("/");
                        curUrl.shift();
                        data = MakeTreeStructure(data, streams[a], curUrl, b);
                    }
                }

                $scope.nodeCount = 0;
                $('#myTree').treeview({data: GetTree(data)});
                $('#myTree').treeview('collapseAll', { silent: true });
                BuildPathSetWidget(response.data.datastreams);
                var curStream = $location.search().ds;

                if(curStream !== undefined){
                    for(var c = 0; c < $scope.nodeCount;c++){
                        var curNode = $('#myTree').treeview('getNode', c);
                        if('info' in curNode && curNode.info.id === parseInt(curStream)){
                            $('#myTree').treeview('revealNode', curNode);
                            $('#myTree').treeview('selectNode', curNode);
                            SelectTreeNode(curNode.info);
                        }
                    }
                }
                $('#myTree').on('nodeSelected', function(event, data) {
                    SelectTreeNode(data.info);
                });
            }, function(error){
                console.log("error occured: " + error);
            });
        }

        function SelectTreeNode(info){
            infoService.resetStreamInfo();
            infoService.setStreamInfo(info);
            $timeout(function(){
                $scope.$apply(function(){
                    $location.search('ds', info.id);
                });
            });
        }

        function GetTree(data){
            var arr = [];
            for(var i in data){
                $scope.nodeCount++;
                var newObj = {
                    "selectable": true,
                    "icon": "glyphicon glyphicon-stop",
                    "color": "#337ab7"
                };
                if(data.constructor === Array){
                    newObj.info = data[i];
                    newObj.text = data[i].name;
                } else {
                    newObj.text = i;
                    newObj.nodes = GetTree(data[i]);
                }
                arr.push(newObj);
            }
            return arr;
        }

        function BuildPathSetWidget(data){
            var val = 0;
            for(var a in data){
                if(data[a].paths.length > val){
                    val = data[a].paths.length;
                }
            }
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

        RequestTree();

}]);