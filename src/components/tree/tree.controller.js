require('./../../../node_modules/bootstrap-treeview/dist/bootstrap-treeview.min.js');

export default class treeController {
    constructor(apiService, $scope, $location) {
        'ngInject';

        this.$scope = $scope;
        this.$location = $location;
        this.apiService = apiService;
    }

    $onInit() {

        this.$scope.treeLoaded = false;
        this.$scope.searchFilter = 'Stream';
        this.$scope.Matches = true;
        this.$scope.isEmpty = false;

        this.LoadData();

        this.$scope.searchInput = () => {
            this.$scope.treeLoaded = false;
            const data = {
                word: this.$scope.searchWords,
                filter: this.$scope.searchFilter,
            };
            if (data.word !== '') {
                this.apiService.get('datastreams/?word=' + data.word + '&filter=' + data.filter)
                    .then((success) => {
                        const pathsArray = this.GeneratePathArray(success.data);
                        const treeStructure = this.MakeTreeStructure(pathsArray);
                        this.RenderTree(treeStructure);
                        this.$scope.isEmpty = false;
                    })
                    .catch((error) => {
                        console.log('error');
                        console.log(error);
                    });
            } else {
                this.$scope.isEmpty = true;
            }
        };
    }

    LoadData() {
        this.apiService.get('datastreams')
            .then((success) => {
                const pathsArray = this.GeneratePathArray(success.data);
                const treeStructure = this.MakeTreeStructure(pathsArray);
                this.RenderTree(treeStructure);
            })
            .catch((error) => {
                console.log(error);
                $('#tree-message').toggleClass('alert-danger');
                $('#tree-message').html('Something went wrong getting data from the server, check the console for details.');
            });
    }

    // [[path, id, name]]
    GeneratePathArray(data) {
        const pathArr = [];
        data.datastreams.forEach((stream) => {
            stream.paths.forEach((path) => {
                pathArr.push([path + '/' + stream.name, stream.id, stream.name]);
            });
        });
        return pathArr;
    }


    MakeTreeStructure(pathsArr) {
        let nodeArray = [];
        this.$scope.nodeCount = 0;
        pathsArr.forEach((path) => {
            const pathArray = path[0].split('/');
            if (pathArray[0] === '') {
                pathArray.shift();
            }
            nodeArray = this.InsertNode(pathArray, path[1], path[2], nodeArray);
        });
        return nodeArray;
    }

    InsertNode(pathArray, streamId, sensorId, nodeArray) {
        this.$scope.nodeCount += 1;
        if (pathArray.length === 1) {
            nodeArray.push({
                text: pathArray[0],
                selectable: true,
                color: '#333',
                id: streamId,
                sensor: sensorId,
            });
            return nodeArray;
        }
        let nodeFound = false;
        for (let i = 0; i < nodeArray.length; i++) {
            if (pathArray[0] === nodeArray[i].text) {
                pathArray.shift();
                if (nodeArray[i].nodes === undefined) {
                    nodeArray[i].nodes = [];
                }

                nodeArray[i].nodes = this.InsertNode(pathArray, streamId, sensorId, nodeArray[i].nodes);
                nodeFound = true;
            }
        }

        if (nodeFound === false) {
            name = pathArray.shift();
            nodeArray.push({
                text: name,
                selectable: false,
                color: '#333',
                nodes: this.InsertNode(pathArray, streamId, sensorId, []),
            });
            return nodeArray;
        }
        return nodeArray;
    }

    RenderTree(data) {
        console.log('start');
        $('#my-tree').treeview({
            data: data,
            showBorder: false,
            color: '#333',
            expandIcon: 'glyphicon glyphicon-folder-close glyphs',
            emptyIcon: 'glyphicon glyphicon-minus',
            collapseIcon: 'glyphicon glyphicon-folder-open glyphs',
        });

        if (this.$scope.nodeCount > 20) {
            $('#my-tree').treeview('collapseAll', {
                silent: true,
            });
        }

        if (this.$scope.nodeCount === 0) {
            this.$scope.Matches = false;
        } else {
            this.$scope.Matches = true;
        }

        $('#my-tree').on('nodeSelected', (event, data) => {
            if (this.$scope.treeLoaded === false) {
                return;
            }
            this.$scope.$apply(() => {
                this.$location.search('datastream', data.id);
            });

        });

        const curStream = parseInt(this.$location.search().datastream);
        if (!isNaN(curStream)) {
            $('#my-tree').treeview('getEnabled', 1).forEach((node) => {
                if (node.id === curStream) {
                    $('#my-tree').treeview('revealNode', node.nodeId);
                    $('#my-tree').treeview('selectNode', node.nodeId);
                }
            });
        }

        if (data.length === 0) {
            $('#graph-message').toggleClass('alert-danger');
            $('#graph-message').html('There are currently no streams available.');
        }
        // Currently just used to stop a digest cycle for selected nodes,
        // This is also the point at which all other graphs can be loaded.
        // TODO: make this a function that spawns the other widgets.
        this.$scope.treeLoaded = true;
    }
}
