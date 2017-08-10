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

            if (hasErrors) {
                return;
            }
            const url = 'datastreams/' + updateData.id;
            const success = this.apiService.put(url, updateData);
            if (success.error === undefined) {
                this.$scope.editing = false;
                location.reload();
            }
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
