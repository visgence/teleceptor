'use strict';

angular.module('teleceptor.timecontroller', ['ui.bootstrap.datetimepicker'])

.controller('timeController', ['$scope', '$location', 'timeService', '$timeout', function($scope, $location, timeService, $timeout){

    $scope.selectTime = function($event, time){
        $($event.target).parent().children().removeClass('active');
        $($event.target).addClass('active');
        $scope.intervalTimer = 10;
        switch(time){
            case 0:
                $location.search('time', 'custom');
                setTimes(null, null);
                 angular.element("#refreshDiv").css("display", "none");
                 refreshing = false;
                break;
            case 1:
                $location.search('time', 'hour');
                setTimes(Date.now() - 3600000, Date.now());
                angular.element("#refreshDiv").css("display", "block");
                refreshing = true;
                break;
            case 2:
                $location.search('time', 'day');
                setTimes(Date.now() - 86400000, Date.now());
                angular.element("#refreshDiv").css("display", "block");
                refreshing = true;
                break;
            case 3:
                $location.search("time", 'week');
                setTimes(Date.now() - 604800000, Date.now());
                angular.element("#refreshDiv").css("display", "block");
                refreshing = true;
                break;
        }
    };

    $scope.SubmitTime = function(){
        $location.search('time', 'custom');
        angular.element("#refreshDiv").css("display", "none");
        setTimes( new Date($('#startdate')[0].value).getTime(), new Date($('#enddate')[0].value).getTime());
    };

    function setTimes(startTime, endTime){
        timeService.setStart(startTime);
        timeService.setEnd(endTime);
        $location.search('startTime', startTime);
        $location.search('endTime', endTime);
    }

    function startUp(){
        var start = $location.search().startTime;
        var end = $location.search().endTime;
        setTimes(start, end);
    }

    $scope.intervalTimer = 10;
    var refreshing = true;

    function IntervalTimer(){
        $timeout(function(){
            if(refreshing === false) return;
            $scope.intervalTimer--;
            if($scope.intervalTimer === 0){
                $location.search('reload', parseInt(Date.now()/1000));
                $scope.intervalTimer = 10;
            }
            IntervalTimer();
        }, 1000);
    }

    $scope.toggleAutoRefresh = function(){
        if(refreshing === true){
            console.log("turn off")
            $scope.intervalTimer = "";
            refreshing = false;
            angular.element("#refreshButton").removeClass("active");
        } else {
            console.log("turn on")
            $scope.intervalTimer = 10;
            refreshing = true;
            IntervalTimer();
            angular.element("#refreshButton").addClass("active");
        }
    };

    IntervalTimer();
    startUp();
}]);