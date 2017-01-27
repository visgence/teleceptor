'use strict';

angular.module('teleceptor.timecontroller', ['ui.bootstrap.datetimepicker'])

.controller('timeController', ['$scope', '$location', 'timeService', '$timeout', function($scope, $location, timeService, $timeout){

    var intervalId;
    $scope.selectTime = function($event, time){
        $($event.target).parent().children().removeClass('active');
        $($event.target).addClass('active');
        $scope.toggleAutoRefresh();
        refreshing = false;
        $timeout(function(){
            $scope.intervalTimer = 10;
            switch(time){
                case 0:
                    $location.search('time', 'custom');
                    setTimes(null, null);
                    $scope.showTimer = false;
                    refreshing = false;
                    clearInterval(intervalId);
                    break;
                case 1:
                    $location.search('time', 'hour');
                    setTimes(Date.now() - 3600000, Date.now());
                    $scope.showTimer = true;
                    refreshing = true;
                    intervalId = setInterval(IntervalTimer, 1000);
                    break;
                case 2:
                    $location.search('time', 'day');
                    setTimes(Date.now() - 86400000, Date.now());
                    $scope.showTimer = true;
                    refreshing = true;
                    intervalId = setInterval(IntervalTimer, 1000);
                    break;
                case 3:
                    $location.search("time", 'week');
                    setTimes(Date.now() - 604800000, Date.now());
                    $scope.showTimer = true;
                    refreshing = true;
                    intervalId = setInterval(IntervalTimer, 1000);
                    break;
            }
        });
        $scope.toggleAutoRefresh();
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
        var type = $location.search().time;
        setTimes(start, end);
        $scope.showTimer =true;
        refreshing = true
        intervalId = setInterval(IntervalTimer, 1000);
        if(type === "custom"){
            clearInterval(intervalId);
            $scope.showTimer =false;
            refreshing = false;
        }

        if(type===undefined){
            type = "day";
        }
        angular.element("#"+type+"Btn").addClass('active');
    }

    $scope.intervalTimer = 10;
    var refreshing = true;

    function IntervalTimer(){
        if(refreshing === false) clearInterval(intervalId);
        $timeout(function(){
        $scope.intervalTimer--;
        if($scope.intervalTimer === 0){
            $location.search('reload', parseInt(Date.now()/1000));
            $scope.intervalTimer = 10;
        }
    });
    }

    $scope.toggleAutoRefresh = function(){
        if(refreshing === true){
            $scope.intervalTimer = "";
            clearInterval(intervalId)
            refreshing = false;
            angular.element("#refreshButton").removeClass("active");
        } else {
            $scope.intervalTimer = 10;
            refreshing = true;
            intervalId = setInterval(IntervalTimer, 1000);
            angular.element("#refreshButton").addClass("active");
        }
    };

    $timeout(function(){
        startUp();
    },100);
}]);