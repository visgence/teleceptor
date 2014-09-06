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


$(document).ready(function(){

    $("form :checkbox").bootstrapSwitch();

});



    Sensor = function(vars) {
        var __this = this;
        var __datacache = {};

        this.uuid             = ko.observable();
        this.sensor_type      = ko.observable();
        this.units            = ko.observable();
        this.name             = ko.observable().extend({required:'Name is required'});
        this.model            = ko.observable();
        this.description      = ko.observable();
        this.last_calibration = ko.observable();
        this.meta_data        = ko.observable();

        this.coefficients = ko.observable(); //used to buffer between this.last_calibration.coefficients and view's JSON

        this.editing = ko.observable(false);

        this.command_value = ko.observable(true); //value to command this sensor to.
        this.command_value.subscribe(function (newValue) {
            console.log("Updating command");
            console.log(newValue);

        });
        $('form :checkbox').on('switchChange.bootstrapSwitch',function(event,state){
            command_value(state);
        });

        this.setCache = function() {
            __datacache = this.toDict();
            __datacache.last_calibration.coefficients = this.coefficients();
            console.log(__datacache);
            console.log(__datacache.last_calibration.coefficients);
        };

        this.restoreCache = function() {
            this.rebuild(__datacache);
        };

        this.checkCoefficients = function() {
            console.log("comparing ");
            console.log(__datacache.last_calibration.coefficients());
            console.log(" to ");
            console.log(this.coefficients())
            return __datacache.last_calibration.coefficients == this.coefficients();
        };


        this.updateError = ko.observable();

        this.display = ko.computed(function() {
            var displayName = __this.name();
            if (displayName === "")
                displayName = __this.uuid();

            return displayName;
        });

        var init = function(vars) {
            vars = vars || {};

            if (vars.hasOwnProperty('uuid'))
                this.uuid(vars.uuid);

            this.rebuild(vars);
        }.bind(this);

        init(vars);
    };

    var updateSuccessCb = function(resp) {
        this.rebuild(resp.sensor);
        this.setCache();
        this.editing(false);
        this.updateError(null);
    };

    var updateFailCb = function(resp,a) {
        var errorMsg = "";
        var errorResp = {};
        console.log(resp);
        console.log(a);

        try{
            errorResp = JSON.parse(resp.responseText);
        }
        catch(e){
            errorMsg = "Sorry, something unexpected occurred.";
        }


        if (errorResp.hasOwnProperty('error'))
            errorMsg = errorResp.error;
        else
            errorMsg = "Sorry, something unexpected occurred.";


        this.updateError(errorMsg);
    };
    Sensor.prototype.update = function() {
        console.log("In update");
        console.log(this.last_calibration().coefficients);
        console.log(this.coefficients());
        this.last_calibration().coefficients = (JSON.parse(this.coefficients()));
        console.log(this.last_calibration().coefficients);
        var id = this.uuid();
        if (!id || !this.validate())
            return $.Deferred().reject().promise();

        var payload = this.toDict();
        delete payload.last_calibration.timestamp;
        console.log("payload:");
        console.log(payload);
        return $.ajax({
               url: "/api/sensors/"+id+"/",
               method: "PUT",
               data: ko.toJSON(payload),
               dataType: "json",
               contentType: "application/json",
               processData: false
        }).then(updateSuccessCb.bind(this),updateFailCb.bind(this));

    };

    Sensor.prototype.updateCommand = function() {
        console.log("Updating command");
        console.log(this.command_value);
    }

    Sensor.prototype.validate = function() {
        var noError = true;

        if (!this.name.validate()) noError = false;
        return noError;
    };

    Sensor.prototype.beginEditing = function() {
        this.setCache();
        this.editing(true);
        console.log(this.last_calibration());
    };

    Sensor.prototype.cancelEditing = function() {
        this.restoreCache();
        this.editing(false);
        this.name.hasError(false);
    };

    Sensor.prototype.rebuild = function(vars) {
        vars = vars || {};

        if (vars.hasOwnProperty('sensor_type'))
            this.sensor_type(vars.sensor_type);
        if (vars.hasOwnProperty('last_calibration')){
            if(typeof(vars.last_calibration.coefficients) == "string")
                this.coefficients(vars.last_calibration.coefficients);
            else
                this.coefficients(ko.toJSON(vars.last_calibration.coefficients));
            this.last_calibration(vars.last_calibration);
        }
        if (vars.hasOwnProperty('units'))
            this.units(vars.units);
        if (vars.hasOwnProperty('name'))
            this.name(vars.name);
        if (vars.hasOwnProperty('model'))
            this.model(vars.model);
        if (vars.hasOwnProperty('description'))
            this.description(vars.description);
        if (vars.hasOwnProperty('meta_data'))
            this.meta_data(vars.meta_data);
    };

    Sensor.prototype.getState = function() {
        var __this = this;
        var id = this.uuid();
        if (!id)
            return $.Deferred().reject().promise();

        return $.get('/api/sensors/'+id, function(resp) {
            __this.rebuild(resp.sensor);
        });
    };

    Sensor.prototype.toDict = function() {
        var returnDict =
        {
            'name':this.name(),
            'description':this.description(),
            'meta_data':this.meta_data(),
            'units':this.units(),
            'last_calibration':this.last_calibration()
        };

        //if(typeof(this.coefficients()) == "string"){
            // returnDict.last_calibration.coefficients = JSON.parse(this.coefficients());
        // }
        // else{
            // returnDict.last_calibration.coefficients = this.coefficients();
        // }

        return returnDict;
    };
