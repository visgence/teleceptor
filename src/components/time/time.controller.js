export default class timeController {

    constructor($scope, $location, $timeout, $interval) {
        'ngInject';

        this.$scope = $scope;
        this.$location = $location;
        this.$timeout = $timeout;
        this.$interval = $interval;
    }

    $onInit() {
        const currentTime = new Date().getTime() / 1000;
        // Initialize date time pickers
        if (this.$location.search().start !== undefined) {
            this.$scope.startDate = new Date(this.$location.search().start * 1000);
        } else {
            this.$scope.startDate = new Date((currentTime - 60 * 60 * 24) * 1000);
        }
        if (this.$location.search().end !== undefined) {
            this.$scope.endDate = new Date(this.$location.search().end * 1000);
        } else {
            this.$scope.endDate = new Date(currentTime * 1000);
        }

        // Check if tab is in selection
        // 1: custom, 2: hour, 3: day, 4: week
        const currentTab = this.$location.search().tab;
        if (currentTab === undefined) {
            this.$scope.tabSelection = 2;
            this.ChangeTab(2);
        }

        this.$scope.SubmitDates = () => {

            const startTime = this.$scope.startDate;
            const endTime = this.$scope.endDate;

            this.$scope.tabSelection = 0;
            this.$location.search('tab', 0);

            if (startTime !== undefined && startTime.toString().length !== 0) {
                this.$location.search('start', new Date(startTime).getTime() / 1000);
            } else {
                this.$location.search('start', null);
            }

            if (endTime !== undefined && endTime.toString().length !== 0) {
                this.$location.search('end', new Date(endTime).getTime() / 1000);
            } else {
                this.$location.search('end', null);
            }
        };

        // 0: custom, 1: hour, 2: day, 3: week
        this.$scope.ChangeQuickTime = (tab) => {
            this.ChangeTab(tab);
        };

        this.$scope.ResetDates = () => {
            this.$timeout(() => {
                this.$scope.$apply(() => {
                    this.$location.search('start', null);
                    this.$location.search('end', null);
                });
            });
        };

        this.$scope.ToggleRefresh = () => {
            if (this.$scope.refresher === undefined) {
                this.$scope.refreshDuration = 5;
                this.$location.search('refresh', 5);
            } else {
                this.$location.search('refresh', null);
            }
        };

        if (this.$location.search().refresh !== undefined) {
            this.$scope.refreshDuration = this.$location.search().refresh;
            this.$scope.refreshEnabled = true;
            this.$scope.refreshProgress = 0;
            this.UpdateRefresh();
        } else {
            this.$scope.refreshEnabled = false;
        }
    }

    ChangeTab(tab) {
        tab = parseInt(tab);
        this.$scope.tabSelection = tab;
        const endTime = parseInt(new Date().getTime());
        let startTime;
        switch (tab) {
            case 1:
                startTime = parseInt(new Date().getTime()) - 1000 * 60 * 60;
                break;
            case 2:
                startTime = parseInt(new Date().getTime()) - 1000 * 60 * 60 * 24;
                break;
            case 3:
                startTime = parseInt(new Date().getTime()) - 1000 * 60 * 60 * 24 * 7;
                break;
            default:
                console.log('big err');
        }
        this.$location.search('tab', tab === 0 ? null : tab);
        this.$location.search('start', parseInt(startTime / 1000));
        this.$location.search('end', parseInt(endTime / 1000));
    }

    UpdateRefresh() {
        if (this.$location.search().refresh === undefined) {
            return;
        }
        this.$timeout(() => {
            this.$scope.refreshProgress += 1;
            if (this.$scope.refreshProgress > 100) {
                const newStart = (parseInt(this.$location.search().start) + this.$scope.refreshDuration);
                const newEnd = (parseInt(this.$location.search().end) + this.$scope.refreshDuration);
                this.$location.search('start', newStart);
                this.$location.search('end', newEnd);
                this.$location.search('refresh', '' + this.$scope.refreshDuration);
            } else {
                this.UpdateRefresh();
            }
            // we take duration, multiply it by 1000 to turn seconds into milliseconds
            // then divide by 100 to get percent of circle completed.
        }, this.$scope.refreshDuration * 10);
    }
}
