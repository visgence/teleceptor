export default class apiService {
    constructor($http) {
        'ngInject';

        this.$http = $http;
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
                const coefficients = data[key].coefficients.split(',');
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
