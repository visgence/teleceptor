export default class streamController {

    constructor(infoService, apiService, $scope, $location) {
        'ngInject';
        this.$scope = $scope;
        this.$location = $location;
        this.apiService = apiService;
        this.infoService = infoService;
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
            this.$scope.stream.forEach((i) => {
                if (i === '-' || i === '') {
                    updateData[i] = null;
                } else if (i === 'paths') {
                    updateData.paths = [];
                    i.forEach((j) => {
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
                        updateData.paths[j] = j.url;
                    });
                } else {
                    updateData[i] = i;
                }
            });

            if (hasErrors) {
                return;
            }
            const url = 'datastream/' + updateData.id;
            this.apiService.post(url, updateData)
                .then((success) => {
                    this.$scope.editing = false;
                    location.reload();
                })
                .catch((error) => {
                    console.log('Error');
                    console.log(error);
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
