export default class streamController {

    constructor(infoService, apiService, $scope, $location, $mdDialog, $mdToast, $interval) {
        'ngInject';
        this.$scope = $scope;
        this.$location = $location;
        this.$interval = $interval;
        this.apiService = apiService;
        this.infoService = infoService;
        this.$mdDialog = $mdDialog;
        this.$mdToast = $mdToast;
    }

    $onInit() {

        this.$scope.stream = {};
        this.$scope.success = true;
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
                            $('#warning-message').css('display', 'block');
                            $('#warning-message').html('Paths must begin with a "/".');
                            hasErrors = true;
                            return;
                        }
                        if (j.url.includes(' ')) {
                            $('#warning-message').css('display', 'block');
                            $('#warning-message').html('Paths cannot have any spaces.');
                            hasErrors = true;
                            return;
                        }
                        updateData.paths.push(j.url);
                    });
                } else {
                    updateData[key] = this.$scope.stream[key];
                }
            });


            const url = 'datastreams/' + updateData.id;
            this.apiService.put(url, updateData)
                .then((success) => {

                    this.$mdToast.show(
                        this.$mdToast.simple()
                            .textContent('Changes Successfully Saved')
                            .position('center top')
                            .hideDelay(1000),
                    );
                    this.$scope.editing = false;
                    this.$interval(() => {
                        location.reload();
                    }, 1200);

                })
                .catch((error) => {
                    this.$mdDialog.show(
                        this.$mdDialog.alert()
                            .parent(angular.element(document.querySelector('#popupContainer')))
                            .clickOutsideToClose(true)
                            .title('Error Saving Fields')
                            .textContent('Error: ' + error)
                            .ariaLabel('Alert Dialog Demo')
                            .ok('Close'),
                    );
                    console.log('Error');
                    console.log(error);
                });
        };
        this.LoadStream();
        console.log(location);

    }

    LoadStream() {
        const curStream = this.$location.search().datastream;
        if (curStream === undefined) {
            return;
        }
        this.apiService.get('datastreams/' + curStream)
            .then((success) => {
                const dataToDisplay = {};
                const stream = success.data.stream;
                Object.keys(stream).forEach((key) => {
                    if (stream[key] === null) {
                        dataToDisplay[key] = '-';
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
                console.log('error');
                console.log(error);
            });
    }
}
