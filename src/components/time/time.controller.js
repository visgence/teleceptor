export default class timeController {

    constructor($scope, $location, $timeout, $interval) {
        'ngInject';

        this.$scope = $scope;
        this.$location = $location;
        this.$timeout = $timeout;
        this.$scope.refreshDisabled = true;
        this.$interval = $interval;
        // global (to the controller) variable to hold the amount of time for refreshes.
        this.refreshIntervalTime = 1000 * 60;
    }

    $onInit() {
        const currentTime = new Date().getTime() / 1000;
        // Initialize date time pickers
        if (this.$location.search().start !== undefined) {
            this.$scope.startDate = new Date(this.$location.search().start * 1000);
        } else {
            this.$scope.startDate = new Date((currentTime - 60 * 60 * 6) * 1000);
        }
        if (this.$location.search().end !== undefined) {
            this.$scope.endDate = new Date(this.$location.search().end * 1000);
        } else {
            this.$scope.endDate = new Date(currentTime * 1000);
        }

        // Check if tab is in selection
        // 1: custom, 2: hour, 3: day, 4: week
        const currentTab = this.$location.search().tab;
        if (currentTab !== undefined) {
            this.ChangeTab(currentTab);
        } else {
            this.$scope.tabSelection = 0;
        }

        // Initialize auto refresh
        if (window.refreshInterval === undefined && this.$location.search().refresh !== undefined) {
            this.SetRefreshInterval();
        }

        this.$scope.SubmitDates = () => {
            const startTime = this.$scope.startDate;
            const endTime = this.$scope.endDate;

            this.$scope.tabSelection = 0;
            this.$location.search('tab', null);

            if (startTime !== undefined && startTime.toString().length !== 0) {
                this.$location.search('start', startTime.getTime() / 1000);
            } else {
                this.$location.search('start', null);
            }

            if (endTime !== undefined && endTime.toString().length !== 0) {
                this.$location.search('end', endTime.getTime() / 1000);
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
            if (window.refreshInterval === undefined) {
                this.SetRefreshInterval();
            } else {
                this.CancelRefreshInterval();
            }
        };

    }

    SetRefreshInterval() {
        this.$timeout(() => {
            this.$scope.refreshTime = 0;
            window.refreshInterval = this.RefreshInterval();
            window.refreshTimer = this.RefreshTimer();
            this.$scope.refreshDisabled = false;
        });
    }

    CancelRefreshInterval() {
        this.$location.search('refresh', null);
        this.$interval.cancel(window.refreshInterval);
        this.$interval.cancel(window.refreshTimer);
        window.refreshInterval = undefined;
        console.log('off');
        this.$scope.refreshDisabled = true;
    }

    RefreshInterval() {
        return this.$interval(() => {
            this.$location.search('refresh', true);
            if (this.$location.search().tab !== undefined) {
                // If we're using a tab, the ChangeTab method can handle all the url updates.
                this.ChangeTab(this.$location.search().tab);
            } else if (this.$location.search().start !== undefined) {
                // if start and end times are defined, just add interval time to them.
                this.$location.search('start', this.$location.search().start + this.refreshTime);
                this.$location.search('end', this.$location.search().end + this.refreshTime);
            } else {
                // If nothing is defined, define new start/end paramaters to start updating.
                this.$location.search('start', new Date().getTime() - 60 * 60 * 6 * 1000);
                this.$location.search('end', new Date().getTime());
            }
        }, this.refreshIntervalTime);
    }

    RefreshTimer() {
        return this.$interval(() => {
            this.$scope.refreshTime += 0.1;
        }, this.refreshIntervalTime / 1000);
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
}
