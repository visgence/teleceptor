import {ShowError} from '../../utilites/dialogs.utils';

export default class treeController {
    constructor(apiService, $scope, $location, $mdDialog, $timeout) {
        'ngInject';

        this.$scope = $scope;
        this.$location = $location;
        this.$mdDialog = $mdDialog;
        this.apiService = apiService;
        this.$timeout = $timeout;
    }

    $onInit() {

        this.$scope.treeLoaded = false;
        this.$scope.searchFilter = 'Stream';
        this.$scope.Matches = true;
        this.$scope.isEmpty = false;
        this.$scope.noStreams = true;

        this.LoadData();

        this.$scope.searchInput = () => {
            this.$scope.treeLoaded = false;
            const data = {
                word: this.$scope.searchWords,
                filter: this.$scope.searchFilter,
            };
            let url = 'datastreams/';
            if (data.word !== '') {
                url += '?word=' + data.word + '&filter=' + data.filter;
            }

            this.apiService.get(url)
                .then((success) => {
                    const pathsArray = this.GeneratePathArray(success.data);
                    const treeStructure = this.MakeTreeStructure(pathsArray);
                    $('#tree-view').jstree();
                    $('#tree-view').jstree().destroy();
                    this.RenderTree(treeStructure);
                    this.$scope.isEmpty = false;
                })
                .catch((error) => {
                    ShowError(this.$mdDialog, error);
                    console.error('Error');
                    console.log(error);
                });
        };
    };


    LoadData() {
        this.apiService.get('datastreams')
            .then((success) => {
                const pathsArray = this.GeneratePathArray(success.data);
                const treeStructure = this.MakeTreeStructure(pathsArray);
                this.RenderTree(treeStructure);
                if ((success.data.datastreams).length !== 0) {
                    this.$scope.noStreams = false;
                }
            })
            .catch((error) => {
                ShowError(this.$mdDialog, error);
                console.error('Error');
                console.log(error);
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
        this.currentSelection = parseInt(this.$location.search().datastream);
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
                sensor: sensorId,
                state: {
                    opened: streamId === this.currentSelection,
                    disabled: false,
                    selected: streamId === this.currentSelection,
                },
                id: streamId,
                icon: '/images/ic_remove_black_18px.svg',
            });
            return nodeArray;
        }
        let nodeFound = false;
        for (let i = 0; i < nodeArray.length; i++) {
            if (pathArray[0] === nodeArray[i].text) {
                pathArray.shift();
                if (nodeArray[i].children === undefined) {
                    nodeArray[i].children = [];
                }

                nodeArray[i].children = this.InsertNode(pathArray, streamId, sensorId, nodeArray[i].children);
                nodeFound = true;
            }
        }

        if (nodeFound === false) {
            name = pathArray.shift();
            nodeArray.push({
                text: name,
                icon: '/images/ic_folder_black_18px.svg',
                children: this.InsertNode(pathArray, streamId, sensorId, []),
            });
            return nodeArray;
        }
        return nodeArray;
    }

    RenderTree(data) {
        if (data.length === 0) {
            this.$scope.noStreams = true;
            return;
        }
        this.$scope.noStreams = false;

        $('#tree-view')
            .on('select_node.jstree', (event, node) => {
                if (node.node.original.id === undefined) {
                    return;
                }
                this.$scope.$apply(() => {
                    this.$location.search('datastream', node.node.original.id);
                });
            })
            .jstree({
                core: {
                    data: data,
                },
                multiple: false,
                // TODO: There is a drag and drop plugin, could be useful for paths setup
                plugins: ['wholerow', 'changed'],
            });
        this.$scope.treeLoaded = true;
    }
}
