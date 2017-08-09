export default class timeController {

    constructor($scope, $location, $timeout) {
        'ngInject';

        this.$scope = $scope;
        this.$location = $location;
        this.$timeout = $timeout;
        this.$scope.internalSelect = true;
    }

    $onInit() {
        // Initialize date time pickers
        if (this.$location.search().start !== undefined) {
            this.$scope.startDate = new Date(this.$location.search().start * 1000);
        }
        if (this.$location.search().end !== undefined) {
            this.$scope.endDate = new Date(this.$location.search().end * 1000);
        }

        // Initialize quick time tabs
        const currentTime = new Date().getTime() / 1000;
        const startTime = this.$location.search().start;
        const endTime = this.$location.search().end;
        this.$scope.tabSelection = 0;
        if (currentTime - endTime < 100 || endTime === undefined) {
            if (currentTime - startTime < 60 * 60 + 100 && currentTime - startTime > 60 * 60 - 100) {
                this.$scope.tabSelection = 1;
            } else if (currentTime - startTime < 24 * 60 * 60 + 100 && currentTime - startTime > 24 * 60 * 60 - 100) {
                this.$scope.tabSelection = 2;
            } else if (currentTime - startTime < 7 * 24 * 60 * 60 + 100 && currentTime - startTime > 7 * 24 * 60 * 60 - 100) {
                this.$scope.tabSelection = 3;
            }
        }

        this.$scope.SubmitDates = () => {
            let startTime = this.$scope.startDate;
            let endTime = this.$scope.endDate;

            if (startTime !== undefined && startTime.toString().length !== 0) {
                startTime = new Date(startTime);
                this.$location.search('start', startTime.getTime() / 1000);
            } else {
                this.$location.search('start', null);
            }

            if (endTime !== undefined && endTime.toString().length !== 0) {
                endTime = new Date(endTime);
                this.$location.search('end', endTime.getTime() / 1000);
            } else {
                this.$location.search('end', null);
            }
        };

        // 1: custom, 2: hour, 3: day, 4: week
        this.$scope.ChangeQuickTime = (tab) => {
            if (this.$scope.internalSelect) {
                return;
            }
            let startTime;
            const endTime = parseInt(new Date().getTime());
            switch (tab) {
                case 2:
                    startTime = parseInt(new Date().getTime()) - 1000 * 60 * 60;
                    break;
                case 3:
                    startTime = parseInt(new Date().getTime()) - 1000 * 60 * 60 * 24;
                    break;
                case 4:
                    startTime = parseInt(new Date().getTime()) - 1000 * 60 * 60 * 24 * 7;
                    break;
            }
            this.$location.search('start', parseInt(startTime / 1000));
            this.$location.search('end', parseInt(endTime / 1000));
        };

        this.$timeout(() => {
            this.$scope.internalSelect = false;
        }, 500);
    }
}
