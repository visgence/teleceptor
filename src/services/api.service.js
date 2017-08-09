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
}
