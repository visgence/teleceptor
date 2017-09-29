import {showError} from '../utilites/dialogs.utils';

export default class apiService {
    constructor($http, $interval, $mdDialog, $mdToast) {
        'ngInject';

        this.$http = $http;

        this.$mdDialog = $mdDialog;
        this.$interval = $interval;
        this.$mdToast = $mdToast;
    }

    get(endpoint) {
        return this.$http.get(`/api/${endpoint}`);
    }
    post(endpoint, data) {
        return this.$http.post(`/api/${endpoint}`, data);
    }
    put(endpoint, data) {
        let cleanedData = data;
        if (endpoint.startsWith('sensors')) {
            cleanedData = this.cleanSensorData(data);
            if (data.error !== undefined) {
                return;
            }
        }
        return this.$http.put(`/api/${endpoint}`, cleanedData);
    }

    cleanSensorData(data) {
        Object.keys(data).forEach((key) => {
            if (key === 'last_calibration') {
                try {
                    const jsonArray = JSON.parse(`{"array${data[key].coefficients}}": `);
                    jsonArray.array.forEach((entry) => {
                        if (isNaN(entry) || entry.constructor === Array) {
                            throw 'Calibration must contain only numbers.';
                        }
                    });
                    data[key].coefficients = jsonArray.array;
                    delete data[key].timestamp;
                } catch (error) {
                    console.log(error);
                    showError(this.$mdDialog, error || 'Calibration is not correctly formatted json.');
                    data.error = true;
                }

            }
        });
        return data;
    }
}
