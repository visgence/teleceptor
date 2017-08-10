export default class apiService {
    constructor($http, $interval, $mdDialog, $mdToast) {
        'ngInject';

        this.$http = $http;

        this.$mdDialog = $mdDialog;
        this.$interval = $interval;
        this.$mdToast = $mdToast;
    }

    get(endpoint) {
        return this.$http.get('/api/' + endpoint);
    }
    post(endpoint, data) {
        this.$http.post('/api/' + endpoint, data)
            .then((success) => {
                return success;
            })
            .catch((error) => {
                return {
                    error: error
                }
            })
    }
    put(endpoint, data) {
        if (endpoint.startsWith('sensors')) {
            data = this.CleanSensorData(data);
        }
        this.$http.put('/api/' + endpoint, data)
            .then((success) => {

                return success
            })
            .catch((error) => {
                console.log(error);
                return {
                    error: error
                }
            })
    }

    ShowSuccess() {
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
    }

    ShowFailure() {
        this.$mdDialog.show(
            this.$mdDialog.alert()
            .parent(angular.element(document.querySelector('#popupContainer')))
            .clickOutsideToClose(true)
            .title('Error Saving Fields')
            .textContent('Error: ' + error)
            .ariaLabel('Alert Dialog Demo')
            .ok('Close'),
        );
    }

    CleanSensorData(data) {
        Object.keys(data).forEach((key) => {
            if (key === 'last_calibration') {

                let coefficients = data[key].coefficients;
                if (coefficients.constructor !== Array) {
                    coefficients = coefficients.split(',');
                }
                const cleanCoefficients = [];
                coefficients.forEach((coef) => {
                    // only allow 0-9, -, .
                    cleanCoefficients.push(coef.replace(/[^0-9\-\.]/g, ''));
                });
                data[key].coefficients = cleanCoefficients.toString();
            }
        });
        return data;
    }
}
