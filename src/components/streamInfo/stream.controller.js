import {ShowSuccess, ShowError} from '../../utilites/dialogs.utils';

export default class streamController {

    constructor(infoService, apiService, $scope, $location, $mdToast, $mdDialog) {
        'ngInject';
        this.$scope = $scope;
        this.$location = $location;
        this.apiService = apiService;
        this.infoService = infoService;
        this.$mdDialog = $mdDialog;
        this.$mdToast = $mdToast;

        $scope.displayInfo = $location.search().datastream !== undefined;
    }

    $onInit() {

        this.$scope.stream = {};
        this.$scope.editing = false;
        this.$scope.ShowInfo = false;

        this.$scope.EditFields = () => {
            $('#warning-message').css('display', 'none');
            this.$scope.editing = true;
        };

        this.$scope.CancelFields = () => {
            this.$scope.editing = false;
        };

        this.$scope.AddPath = () => {
            this.$scope.stream.paths.push({
                url: '/new_path_' + this.$scope.stream.paths.length,
            });
        };

        this.$scope.SaveFields = () => {
            const updateData = {};
            let hasErrors = false;
            Object.keys(this.$scope.stream).forEach((key) => {
                if (this.$scope.stream[key] === '-' || this.$scope.stream[key] === '') {
                    updateData[key] = null;
                } else if (key === 'paths') {
                    updateData.paths = [];
                    this.$scope.stream[key].forEach((j) => {
                        if (j.url === '') {
                            return;
                        }
                        if (!j.url.startsWith('/')) {
                            ShowError(this.$mdDialog, 'Paths must begin with a "/".');
                            hasErrors = true;
                            return;
                        }
                        if (j.url.includes(' ')) {
                            ShowError(this.$mdDialog, 'Paths cannot have any spaces.');
                            hasErrors = true;
                            return;
                        }
                        updateData.paths.push(j.url);
                    });
                } else if (key === 'min_value' || key === 'max_value') {
                    if (isNaN(this.$scope.stream[key])) {
                        ShowError(this.$mdDialog, 'Min and Max values must be a number');
                        hasErrors = true;
                        return;
                    }
                    updateData[key] = this.$scope.stream[key];
                } else {
                    updateData[key] = this.$scope.stream[key];
                }
            });

            if (hasErrors) {
                return;
            }
            const url = 'datastreams/' + updateData.id;
            this.apiService.put(url, updateData)
                .then((success) => {
                    this.infoService.setStream(success.data.stream);
                    ShowSuccess(this.$mdToast);
                    this.$scope.editing = false;
                })
                .catch((error) => {
                    ShowError(this.$mdDialog, error);
                });
        };
        this.LoadStream();
    }

    LoadStream() {
        const curStream = this.$location.search().datastream;
        if (curStream === undefined) {
            return;
        }
        this.apiService.get('datastreams/' + curStream)
            .then((success) => {
                if (success.data.error !== undefined) {
                    ShowError(this.$mdDialog, success.data.error);
                    return;
                }
                const dataToDisplay = {};
                const stream = success.data.stream;
                Object.keys(stream).forEach((key) => {
                    if (stream[key] === null) {
                        dataToDisplay[key] = '';
                    } else if (key === 'paths') {
                        dataToDisplay.paths = [];
                        stream[key].forEach((path) => {
                            dataToDisplay.paths.push({
                                url: path,
                            });
                        });
                    } else {
                        dataToDisplay[key] = stream[key];
                    }
                });
                this.$scope.stream = dataToDisplay;
                this.$scope.ShowInfo = true;
                this.infoService.setStream(stream);
                $('#stream-card').css('visibility', 'visible');
            })
            .catch((error) => {
                ShowError(this.$mdDialog, error);
            });
    }
}