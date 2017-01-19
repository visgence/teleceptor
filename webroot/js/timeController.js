'use strict';

angular.module('teleceptor.timecontroller', ['ui.bootstrap.datetimepicker'])

.controller('timeController', ['$scope', '$location', 'timeService', function($scope, $location, timeService){

    $scope.selectTime = function($event, time){
        $($event.target).parent().children().removeClass('active');
        $($event.target).addClass('active');
        switch(time){
            case 0:
                $location.search('time', 'custom');
                setTimes(null, null);
                break;
            case 1:
                $location.search('time', 'hour');
                setTimes(Date.now() - 3600000, Date.now());
                break;
            case 2:
                $location.search('time', 'day');
                setTimes(Date.now() - 86400000, Date.now());
                break;
            case 3:
                $location.search("time", 'week');
                setTimes(Date.now() - 604800000, Date.now());
                break;
        }
    };

    $scope.SubmitTime = function(){
        $location.search('time', 'custom');
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
    startUp()
}]);