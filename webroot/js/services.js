/*jslint node: true */
'use strict';

angular.module('teleceptor.services', [])

.factory('timeService', function() {
    var values = {
        start: null,
        end: null
    };

    return {
        values: values,
        getValues: function() {
            return values;
        },
        setStart: function(newStart) {
            values.start = parseInt(newStart);
        },
        setEnd: function(newEnd) {
            values.end = parseInt(newEnd);
        }
    };
})

.factory('infoService', function() {
    var sensorInfo;
    var streamInfo;
    var readingsInfo;

    return {
        streamInfo: streamInfo,
        sensorInfo: sensorInfo,
        getStreamInfo: function() {
            return streamInfo;
        },
        setStreamInfo: function(newInfo) {
            streamInfo = newInfo;
        },
        resetStreamInfo: function() {
            streamInfo = null;
        },
        getSensorInfo: function() {
            return sensorInfo;
        },
        setSensorInfo: function(newInfo) {
            sensorInfo = newInfo;
        },
        resetSensorInfo: function() {
            sensorInfo = null;
        },
        getReadingsInfo: function() {
            return readingsInfo;
        },
        setReadingsInfo: function(newInfo) {
            readingsInfo = newInfo;
        },
        resetReadingsInfo: function() {
            readingsInfo = null;
        }
    };
})

.factory('apiService', ['$http', function($http) {
    var urlBase = '/api/';
    var apiService = {};

    apiService.get = function(Str) {
        return $http.get(urlBase + Str);
    };

    apiService.put = function(Str, params) {
        return $http.put(urlBase + Str, params);
    };

    apiService.post = function(Str, params) {
        return $http.post(urlBase + Str, params);
    };

    return apiService;
}]);
