/*jslint node: true */
'use strict';

var angular, $;
angular.module('teleceptor.timecontroller', ['ui.bootstrap.datetimepicker'])

.controller('timeController', ['$scope', '$location', 'timeService', '$timeout', function($scope, $location, timeService, $timeout){

    var intervalId;
    $scope.selectTime = function($event, time){
        $($event.target).parent().children().removeClass('active');
        $($event.target).addClass('active');
        refreshing = false;
        clearInterval(intervalId);
        $('#startdate')[0].value = "";
        $('#enddate')[0].value = "";
        $timeout(function(){
            $scope.intervalTimer = 60;
            switch(time){
                case 0:
                    $location.search('time', 'custom');
                    setTimes(null, null);
                    $scope.showTimer = false;
                    break;
                case 1:
                    $location.search('time', 'hour');
                    setTimes(Date.now() - 3600000, Date.now());
                    $scope.showTimer = true;
                    break;
                case 2:
                    $location.search('time', 'day');
                    setTimes(Date.now() - 86400000, Date.now());
                    $scope.showTimer = true;
                    break;
                case 3:
                    $location.search("time", 'week');
                    setTimes(Date.now() - 604800000, Date.now());
                    $scope.showTimer = true;
                    break;
            }
        });
    };

    $scope.SubmitTime = function(){
        angular.element("#hourBtn").removeClass('active');
        angular.element("#dayBtn").removeClass('active');
        angular.element("#weekBtn").removeClass('active');
        angular.element("#customBtn").addClass('active');
        angular.element("#refreshDiv").css("display", "none");
        $location.search('time', 'custom');
        setTimes(new Date($('#startdate')[0].value).getTime(), new Date($('#enddate')[0].value).getTime());
    };

    function setTimes(startTime, endTime){
        if(isNaN(startTime) && isNaN(endTime)){
            startTime = Date.now() - 86400000;
            endTime = Date.now();
        } else if(isNaN(startTime)){
            startTime = endTime - 86400000;
        } else if(isNaN(endTime)){
            endTime = startTime + 86400000;
        }

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
        refreshing = false;
        if(type === "custom"){
            clearInterval(intervalId);
            $scope.showTimer =false;
        }
        if(type===undefined) type = "day";
        angular.element("#"+type+"Btn").addClass('active');
    }

    $scope.intervalTimer = 60;
    var refreshing = true;

    function IntervalTimer(){
        if(refreshing === false) clearInterval(intervalId);
        $timeout(function(){
            $scope.intervalTimer--;
            if($scope.intervalTimer === 0){
                $location.search('reload', parseInt(Date.now()/1000));
                $scope.intervalTimer = 60;
            }
        });
    }

    $scope.toggleAutoRefresh = function(){
        if(refreshing === true){
            $scope.intervalTimer = "";
            clearInterval(intervalId);
            refreshing = false;
            angular.element("#refreshButton").removeClass("active");
        } else {
            $scope.intervalTimer = 60;
            refreshing = true;
            intervalId = setInterval(IntervalTimer, 1000);
            angular.element("#refreshButton").addClass("active");
        }
    };

    $timeout(function(){
        startUp();
    },100);
}]);