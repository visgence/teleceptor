'use strict';

angular.module('teleceptor.treecontroller', [])

.controller('treeController', ['$scope', '$location', '$http', '$compile', 'apiService', 'infoService', function($scope, $location, $http, $compile, apiService, infoService){
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
            var pathSetId = 0;
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

                var curTree = {}
                var treeData = GetTree(data);
                $('#myTree').treeview({data: GetTree(data)});

                $('#myTree').treeview('collapseAll', { silent: true });
                BuildPathSetWidget(response.data.datastreams);
                var curStream = $location.search().ds;


                if(curStream !== undefined){
                    var myQ = [$('#myTree').treeview('getNode', 0)];
                    var used = [];
                    var allNodes = [];
                    while(myQ.length > 0){
                        var cur = myQ.shift();
                        var already = false;
                        for(var d in used){
                            if(used[d] === cur.text){
                                already = true;
                            }
                        }
                        if(already) continue;
                        myQ.push($('#tree').treeview('getSiblings', cur.nodeId));
                        for(var b in cur.nodes){
                            myQ.push(cur.nodes[b]);
                        }
                        used.push(cur.text);
                    }


                    for(var c in $('#tree').treeview){
                        if(nodes[c].info.id === curStream){
                            $('#myTree').treeview('revealNode', [parseInt(nodes[c].nodeId)]);
                            $('#myTree').treeview('selectNode', [nodes[c].nodeId]);
                        }
                    }
                //     for(var i = 0; i <$scope.idData.paths.length+Object.keys($scope.idData.pathSets[$scope.pathSetSelection]).length; i++){
                //         var node = $('#myTree').treeview('getNode', [i]);
                //         if(node.sensor   == curNode){
                //             $('#myTree').treeview('revealNode', [parseInt(node.nodeId)]);
                //             $('#myTree').treeview('selectNode', [node.nodeId]);
                //         }
                //     }
                }
                $('#myTree').on('nodeSelected', function(event, data) {
                    infoService.resetStreamInfo();
                    infoService.setStreamInfo(data.info);
                    $scope.$apply(function(){
                        $location.search('ds', data.info.id);
                    });
                });

            }, function(error){
                console.log("error occured: " + error);
            });
        }

        function GetTree(data){
            var arr = [];
            for(var i in data){
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