/*
    (c) 2014 Visgence, Inc.

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>
*/

    var TimeControls = function(vars) {
        var __this = this;

        //Default options for datetimepickers
        var dtOptions = {};

        //Reference to datetimepickers
        var startPicker = null;
        var endPicker   = null;

        //Extend these to hold the values from the input fields as epoch seconds.
        this.startRange = ko.observable().extend({epoch: null});
        this.endRange   = ko.observable().extend({epoch: null});

        this.isBusy = ko.observable(false);

        // Allows us to subscribe to either the start or end changing or both.
        //We throttle the computed so it doesn't fire twice should we set start and end one right after the other.
        this.timeRange = ko.computed(function() {
            var start = this.startRange.epochValue();
            var end   = this.endRange.epochValue();
            var newRange = {'start': start, 'end': end};

            return newRange;
        }, this);


        //Numeric value to wait by before refreshing
        this.refreshRate = ko.observable().extend({numeric: {'precision': 0, 'default': 10}});
        this.refreshCountdown = ko.observable();
        this.autoRefresh = ko.observable();


        //Time options for quick link buttons to pre-set start/end inputs
        var customTimeOption  = {"display": "Custom", "identifier": "custom",  "action": this.custom};
        var lastHourOption    = {"display": "Hour",   "identifier": "hour",    "action": this.lastHour};
        var last24HoursOption = {"display": "Day",    "identifier": "24-hour", "action": this.last24Hours};
        var lastWeekOption    = {"display": "Week",   "identifier": "week",    "action": this.lastWeek};
        var defaultTimeOption = last24HoursOption;

        this.timeOptions  = ko.observableArray([customTimeOption, lastHourOption, last24HoursOption, lastWeekOption]);

        //The currently selected time option button
        this.selectedTime = ko.observable(defaultTimeOption);

        //Lets us know if the custom time option is the one selected
        this.isCustomSelected = ko.computed(function() {
            var selectedTime = this.selectedTime();
            if (selectedTime === undefined || !selectedTime.hasOwnProperty('identifier'))
                return false;

            return selectedTime.identifier === "custom" ? true : false;
        }, this);


        //Initialize the datetimepickers
        var setupPickers = function(ele) {
            var initialStart = __this.startRange.epochValue();
            var initialEnd = __this.endRange.epochValue();

            var startOptions = $.extend({}, dtOptions);
            var endOptions = $.extend({}, dtOptions);

            if (initialStart)
                endOptions['startDate'] = new Date(initialStart * 1000);
            if (initialEnd)
                startOptions['endDate'] = new Date(initialEnd * 1000);

            startPicker = $(ele).find('.range-start').datetimepicker(startOptions)
            .on('dp.change', function(e) {
                $(endPicker).data('DateTimePicker').setMinDate(e.date);
            });

            endPicker = $(ele).find('.range-end').datetimepicker(endOptions)
            .on('dp.change', function(e) {
                $(startPicker).data('DateTimePicker').setMaxDate(e.date);
            });

            if (initialStart)
                $(startPicker).data("DateTimePicker").setDate(moment(initialStart*1000));
            if (initialEnd)
                $(endPicker).data("DateTimePicker").setDate(moment(initialEnd*1000));

            __this.startRange.epochValue.subscribe(setEpochHandler.bind(startPicker));
            __this.endRange.epochValue.subscribe(setEpochHandler.bind(endPicker));
        };

        var setEpochHandler = function(epoch) {
            if (!epoch)
                return;

            if (typeof(epoch) == "string")
                epoch = parseInt(epoch);

            $(this).data("DateTimePicker").setDate(moment(epoch*1000));
        };

        var timeRangeHandler = function(newRange) {
            var timeOption = __this.selectedTime();
            newRange['time'] = timeOption.identifier;
            $(__this).trigger('rangechanged', newRange);
            console.log("range just changed");
        };

        var autoRefreshHandler = function() {
            var autoRefresh = __this.autoRefresh();

            if (autoRefresh)
                __this.restartRefreshInterval();
            else
                __this.stopRefreshInterval();
        };

        var intervalId = null;
        this.stopRefreshInterval = function() {
            clearInterval(intervalId);
        };

        this.restartRefreshInterval = function() {
            if (!this.autoRefresh())
                return;

            var rate = __this.refreshRate();
            __this.refreshCountdown(rate);

            clearInterval(intervalId);
            intervalId = setInterval(function() {
                //Make sure we don't fetch data if we're already fetching data
                if (!__this.isBusy()) {
                    var countdown = __this.refreshCountdown();
                    if (countdown > 0) {
                        __this.refreshCountdown(countdown - 1);
                        return;
                    }
                    __this.activateSelectedTime();
                    __this.refreshCountdown(rate);
                }
            }, 1000);
        };

        var init = function(vars) {
            __this.rebuild(vars);
            setupPickers($(".graph-time-controls"));
            __this.timeRange.subscribe(timeRangeHandler);

             //On page load set the Default Time
            if (vars.hasOwnProperty('time')) {
                __this.selectTime(vars['time']);
            }
            else{
                __this.selectTime("24-hour");
            }

            //Throttle the amount computed pops off subscribers sense it's evaluating two observables.
            //IMPORTANT!! This has to be done here. Otherwise the throttle stalls when values are being set
            //initially and causes subscriptions to pop off late messing up the graphs.
            __this.timeRange = __this.timeRange.extend({throttle: 25});

            //We want to reset the auto refresh interval counter when anything regarding it changes
            __this.autoRefresh.subscribe(autoRefreshHandler);
            if (!__this.isCustomSelected())
                __this.autoRefresh(true);
            else
                __this.autoRefresh(false);

            __this.isBusy.subscribe(function(busy) {
                if (!busy)
                    __this.restartRefreshInterval();

            });

        };

        init(vars);
    };


    TimeControls.prototype.autoRefreshToggle = function() { this.autoRefresh(!this.autoRefresh()); };

    TimeControls.prototype.setLastSeconds = function(amount) {
        var now = (new Date()).getTime() / 1000;
        var lastHour = now - amount;

        this.startRange.epochValue(Math.round(lastHour));
        this.endRange.epochValue(Math.round(now));
    };

    TimeControls.prototype.lastHour    = function() { this.setLastSeconds(3600); };
    TimeControls.prototype.last24Hours = function() { this.setLastSeconds(86400); };
    TimeControls.prototype.lastWeek    = function() { this.setLastSeconds(604800); };
    TimeControls.prototype.custom      = function() {
        var timeOption = this.selectedTime();
        $(this).trigger('timechanged', {time: timeOption.identifier});
        this.autoRefresh(false);
    };

    TimeControls.prototype.selectTime = function(timeOption, preventDefault) {
        if (typeof(timeOption) == "string") {
            $.each(this.timeOptions(), function() {
                if (timeOption === this.identifier) {
                    timeOption = this;
                    return true;
                }
            });

            if (typeof(timeOption) == "string")
                throw "Couldn't find an appropriate time options to select";
        }

        if (this.isCustomSelected() && timeOption.identifier !== "custom")
            this.autoRefresh(true);

        this.selectedTime(timeOption);
        if (!preventDefault && timeOption.hasOwnProperty('action') && timeOption.action !== null) {
            timeOption.action.call(this);
            this.restartRefreshInterval();
        }
    };

    TimeControls.prototype.activateSelectedTime = function() {
        var timeOption = this.selectedTime();
        if (timeOption.hasOwnProperty('action') && timeOption.action !== null){
            timeOption.action.call(this);
        }
    };

    TimeControls.prototype.rebuild = function(vars) {
        vars = vars || {};

        //We don't want to set start/end if we dont' have to.  Keeps subscriptions from popping off.
        if (vars.hasOwnProperty('start') && this.startRange.epochValue() != vars.start)
            this.startRange.epochValue(vars['start']);
        if (vars.hasOwnProperty('end') && this.endRange.epochValue() != vars.end)
            this.endRange.epochValue(vars['end']);

        if (!this.startRange.epochValue())
            this.startRange('');
        if (!this.endRange.epochValue())
            this.endRange('');

        if (vars.hasOwnProperty('time'))
            this.selectTime(vars['time'], true);
    };

    TimeControls.prototype.dispose = function() {
        this.stopRefreshInterval();
    };
