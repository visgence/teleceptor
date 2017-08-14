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
        return this.$http.post('/api/' + endpoint, data);
    }
    put(endpoint, data) {
        if (endpoint.startsWith('sensors')) {
            data = this.CleanSensorData(data);
        }
        return this.$http.put('/api/' + endpoint, data);
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
                    cleanCoefficients.push(parseFloat(coef.toString().replace(/[^0-9\-\.]/g, '')));
                });
                console.log(cleanCoefficients);
                data[key].coefficients = cleanCoefficients;
            }
        });
        return data;
    }
}
