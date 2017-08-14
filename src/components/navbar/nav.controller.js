export default class graphController {
    constructor($scope) {
        'ngInject';
        this.$scope = $scope;
    }

    $onInit() {

        this.$scope.versionNumber = window.version;
    }
}
