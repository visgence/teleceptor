/*jslint node: true */
'use strict';

angular.module('teleceptor.treecontroller', [])

.controller('treeController', ['$scope', '$location', '$http', '$compile', 'apiService', 'infoService', '$timeout', '$window', function($scope, $location, $http, $compile, apiService, infoService, $timeout, $window) {
    $scope.pathSetSelection = $location.search().pathSet;
    if ($scope.pathSetSelection === undefined) {
        $scope.pathSetSelection = 0;
    }

    $scope.ChangePath = function(e) {
        if (e == "next")
            e = $scope.pathSetSelection + 1;
        if (e == "previous") {
            e = $scope.pathSetSelection - 1;
        }
        $scope.pathSetSelection = e;
        $location.search('pathSet', e);

        RequestTree();
    };

    $scope.$on('$routeUpdate', function() {
        var nodeFound = false;
        var i = 0;
        var ds = $location.search().ds;
        var source = $location.search().source;
        while (!nodeFound && i < 500) {
            i++;
            var node = $('#myTree').treeview('getNode', i);
            if (node.info === undefined) continue;
            if (source !== node.info.source) continue;
            if (parseInt(ds) !== parseInt(node.info.id)) continue;
            $('#myTree').treeview('selectNode', [i, { silent: true }]);
            $('#myTree').treeview('revealNode', [i, { silent: true }]);
            infoService.resetStreamInfo();
            infoService.setStreamInfo(node.info);
            break;
        }
    });

    function MakeTreeStructure(data, stream, curUrl, pathId) {
        if (curUrl.length === 1) {
            if (!(curUrl[0] in data)) data[curUrl[0]] = [];
            stream.pathId = pathId;
            data[curUrl[0]].push(stream);
            return data;
        }
        if (!(curUrl[0] in data)) data[curUrl[0]] = {};
        var temp = curUrl.shift();
        data[temp] = MakeTreeStructure(data[temp], stream, curUrl, pathId);
        return data;
    }

    function RequestTree() {
        var pathSetId = $location.search().pathSet - 1;
        if (isNaN(pathSetId)) pathSetId = 0;
        apiService.get('datastreams').then(function(response) {
            var streams = response.data.datastreams;

            var data = {};

            for (var a in streams) {
                for (var b in streams[a].paths) {
                    if (parseInt(b) !== pathSetId) continue;
                    var curUrl = streams[a].paths[b].split("/");
                    curUrl.shift();
                    data = MakeTreeStructure(data, streams[a], curUrl, b);
                }
            }

            $scope.nodeCount = 0;

            $('#myTree').treeview({
                data: GetTree(data),
                showBorder: false,
                color: "#333",
                expandIcon: "glyphicon glyphicon-folder-close glyphs",
                emptyIcon: "glyphicon glyphicon-minus",
                collapseIcon: "glyphicon glyphicon-folder-open glyphs"

            });
            $('#myTree').treeview('collapseAll', { silent: true });
            BuildPathSetWidget(response.data.datastreams);
            var curStream = $location.search().ds;

            var currentPathSet = $location.search().pathSet;
            if (currentPathSet === undefined) currentPathSet = 1;

            if (curStream !== undefined) {
                for (var c = 0; c < $scope.nodeCount; c++) {
                    var curNode = $('#myTree').treeview('getNode', c);
                    if ('info' in curNode && curNode.info.id === parseInt(curStream)) {
                        $('#myTree').treeview('revealNode', curNode);
                        $('#myTree').treeview('selectNode', curNode);
                        SelectTreeNode(curNode.info);
                    }
                }
            }

            $('#myTree').on('nodeSelected', function(event, data) {
                if (data.info === undefined) {
                    $('#myTree').treeview('expandNode', [data.nodeId, { levels: 2, silent: true }]);
                } else {
                    SelectTreeNode(data.info);
                }
            });

            $('#myTree').on('nodeUnselected', function(event, data) {
                if (data.info === undefined) {
                    $('#myTree').treeview('collapseNode', [data.nodeId, { levels: 2, ignoreChildren: false }]);
                }
            });

            if (streams.length === 0) {
                $('#myTree').text("There are currently no streams available.");
            }

        }, function(error) {
            console.log("error occured: " + error);
        });
    }

    function SelectTreeNode(info) {
        if (info === undefined) return;
        infoService.resetStreamInfo();
        infoService.setStreamInfo(info);
        $timeout(function() {
            $scope.$apply(function() {
                $location.search('ds', info.id);
            });
        });
    }

    function GetTree(data) {
        var arr = [];
        for (var i in data) {
            $scope.nodeCount++;
            var newObj = {
                "color": "#333"
            };
            if (data.constructor === Array) {
                newObj.info = data[i];
                newObj.text = data[i].name;
                newObj.selectable = true;
            } else {
                newObj.text = i;
                newObj.nodes = GetTree(data[i]);
                newObj.selectable = false;
            }
            arr.push(newObj);
        }
        return arr;
    }

    function BuildPathSetWidget(data) {
        var val = 0;
        for (var a in data) {
            if (data[a].paths.length > val) {
                val = data[a].paths.length;
            }
        }
        if (val <= 1) return;
        var button = "<li><a href='#'></a></li>";
        var wrapper = "<nav aria-label='Page navigation'><ul class='pagination'>";
        var currentSet = $location.search().pathSet;
        if (currentSet === undefined) currentSet = 1;
        for (var i = 0; i < val; i++) {
            if (i > 7) {
                //make arrows and break;
                break;
            }
            var newButton = "<li><button class='btn btn-default";
            if (currentSet - 1 === i) newButton += " active";
            newButton += "' ng-click=ChangePath(" + (i + 1) + ")>" + (i + 1) + "</button></li>";
            wrapper += newButton;
        }
        angular.element('#pathSetPaginator').html("");

        angular.element('#pathSetPaginator').append($compile(wrapper)($scope));
    }
    RequestTree();
}]);
