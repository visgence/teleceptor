export default class graphController {
    constructor($scope) {
        'ngInject';
        this.$scope = $scope;
    }

    $onInit() {
        this.$scope.versionNumber = window.version;
        const versionDate = window.buildDate;
        this.$scope.buildDate = new Date(versionDate * 1000).toDateString();
    }
}
