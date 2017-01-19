angular.module('teleceptor.services', [])

.factory('timeService', function(){
    var values = {
        start: null,
        end: null
    };

    return {
        values: values,
        getValues: function(){
            return values;
        },
        setStart: function(newStart){
             values.start = parseInt(newStart);
        },
        setEnd: function(newEnd){
            values.end = parseInt(newEnd);
        }
    };
})

.factory('infoService', function(){
    var info = [];

    return {
        info: info,
        getInfo: function(){
            return info;
        },
        setInfo: function(newInfo){
            info = newInfo;
        }
    };
})

.factory('apiService', ['$http', function($http){
    var urlBase = '/api/';
    var apiService = {};

    apiService.get = function(Str){
        console.log("posting get to " + urlBase+Str)
        return $http.get(urlBase+Str);
    };

    return apiService;
}]);