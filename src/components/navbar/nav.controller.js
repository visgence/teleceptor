import packageJSON from '../../../package';

export default class graphController {
    constructor($scope) {
        'ngInject';
        this.$scope = $scope;
    }

    $onInit() {
        this.$scope.versionNumber = packageJSON.version;
        this.$scope.buildDate = packageJSON.date;
    }
}
