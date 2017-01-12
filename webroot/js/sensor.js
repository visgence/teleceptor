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


    Sensor = function(vars) {
        var __this = this;
        var __datacache = {};
        var __firstrun = true;

        this.uuid               = ko.observable();
        this.sensor_type        = ko.observable();
        this.units              = ko.observable();
        this.name               = ko.observable().extend({required:'Name is required'});
        this.model              = ko.observable();
        this.description        = ko.observable();
        this.last_calibration   = ko.observable();
        this.lastCalibration    = ko.observable();
        this.meta_data          = ko.observable();
        this.isInput            = ko.observable();
        this.temp_command_value = ko.observable()
        this.new_data_value     = ko.observable()
        this.coefficients       = ko.observable(); //used to buffer between this.last_calibration.coefficients and view's JSON
        this.editing            = ko.observable(false);
        this.command_value      = ko.observable(true); //value to command this sensor to.
        this.post_value         = ko.observable();
        this.errorMessage = ko.observable();

        this.streamUuid = ko.observable();
        this.streamName = ko.observable();
        this.streamDescription = ko.observable();
        this.streamEditing = ko.observable();
        this.paths = ko.observableArray();

        this.updateSuccessCb = function(resp) {
            __this.rebuild(resp.sensor);
            __this.editing(false);
            __this.streamEditing(false);
            __this.updateError(null);
            $(__this).trigger('calibrationchanged')
        };

        this.commandSuccessCb = function(resp){
            __this.rebuild(resp.sensor);
            __this.editing(false);
            __this.updateError(null);
            __this.errorMessage(null);
        }

        this.sendSuccessCb = function(resp){
            __this.rebuild(resp.sensor);
            __this.updateError(null);
        }

        this.updateFailCb = function(resp,a) {
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

        this.sendCommand = function(){
            this.command_value(parseFloat(this.temp_command_value()));
        };

        this.sendData = function(){
            this.post_value(parseFloat(this.new_data_value()));
        };



        this.exportData = function(){
            //Use jQuery to get graph script's variables
            console.log($(SensorsIndex));
            console.log($(graph));
            var start_time = $(document).graph.rangeStart();
            var end_time = $(document).graph.rangeEnd();
            this.export_data(start_time, end_time);
        };

        this.post_value.subscribe(function (newValue){
            var id = __this.uuid();
            if (!id || !__this.validate())
                return $.Deferred().reject().promise();

            var time = (new Date()).getTime() / 1000;
            sensorReading = {"name": id, "sensor_type": __this.sensor_type(),
             "timestamp": time, "meta_data":{}};
            payload = [{
                "info":{"uuid": "", "name":__this.name(), "description": __this.description(), "out": (__this.isInput() ? [] : [sensorReading]),
                "in": (__this.isInput() ? [sensorReading] : [])}, "readings": [[id, newValue, time]]
            }];
            console.log(payload);
            return $.ajax({
               url: "/api/station/",
               method: "POST",
               data: ko.toJSON(payload),
               dataType: "json",
               contentType: "application/json",
               processData: false
            }).then(__this.sendSuccessCb.bind(__this),__this.updateFailCb.bind(__this));

        });

        this.command_value.subscribe(function (newValue) {
            if (__firstrun){
                __firstrun = false;
                return;
            }
            //post new value to commands api
            payload = {
                "message": __this.command_value()
               ,"duration": 60000
            };
            console.log(payload);
            var id = __this.uuid();
            if (!id || !__this.validate())
                return $.Deferred().reject().promise();
            return $.ajax({
               url: "/api/messages/"+id+"/",
               method: "POST",
               data: ko.toJSON(payload),
               dataType: "json",
               contentType: "application/json",
               processData: false
            }).then(__this.commandSuccessCb.bind(__this),__this.updateFailCb.bind(__this));
            console.log("Updating command");
            console.log(newValue);

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

        this.addStreamPath = function(){
            if(this.paths === null){
                this.paths = [];
            }
            this.paths.push("");
        };

        var init = function(vars) {
            vars = vars || {};

            if (vars.hasOwnProperty('uuid'))
                this.uuid(vars.uuid);

            this.rebuild(vars);
        }.bind(this);

        init(vars);

    };
    Sensor.prototype.update = function() {
        this.last_calibration().coefficients = (JSON.parse(this.coefficients()));
        var id = this.uuid();
        if (!id || !this.validate())
            return $.Deferred().reject().promise();

        var payload = this.toDict();
        delete payload.last_calibration.timestamp;
        return $.ajax({
               url: "/api/sensors/"+id+"/",
               method: "PUT",
               data: ko.toJSON(payload),
               dataType: "json",
               contentType: "application/json",
               processData: false
        }).then(this.updateSuccessCb.bind(this),this.updateFailCb.bind(this));
    };

    Sensor.prototype.streamUpdate = function() {
        var id = this.streamUuid();
        if (!id || !this.validate())
            return $.Deferred().reject().promise();
        if(!this.checkPaths()){
            this.DisplayWarning('paths must start with a "/" and cannot end with a "/"', 4);
            return;
        }
        var payload = this.streamToDict();
        console.log(payload);
        return $.ajax({
               url: "/api/datastreams/"+id+"/",
               method: "PUT",
               data: ko.toJSON(payload),
               dataType: "json",
               contentType: "application/json",
               processData: false,
               success: function(){location.reload();}
        }).then(this.updateSuccessCb.bind(this),this.updateFailCb.bind(this));
    };

    Sensor.prototype.updateCommand = function() {
        console.log("Updating command");
        console.log(this.command_value);
    };

    Sensor.prototype.validate = function() {
        var noError = true;

        if (!this.name.validate()) noError = false;
        return noError;
    };

    Sensor.prototype.beginEditing = function() {
        this.setCache();
        this.editing(true);
    };

    Sensor.prototype.cancelEditing = function() {
        this.restoreCache();
        this.editing(false);
        this.name.hasError(false);
    };

    Sensor.prototype.deleteStream = function() {
        var id = this.streamUuid();
        if (!id || !this.validate())
            return $.Deferred().reject().promise();

        var payload = this.streamToDict();
        return $.ajax({
               url: "/api/readings/"+id+"/",
               method: "DELETE",
               data: ko.toJSON(payload),
               dataType: "json",
               contentType: "application/json",
               processData: false,
               success: function(data){
                    return $.ajax({
                       url: "/api/datastreams/"+id+"/",
                       method: "DELETE",
                       data: ko.toJSON(payload),
                       dataType: "json",
                       contentType: "application/json",
                       processData: false,
                       success: function(data){
                            window.location.href = window.location.pathname;
                       }
                });
               }
        }).then(this.updateSuccessCb.bind(this),this.updateFailCb.bind(this));
    };

    Sensor.prototype.streamBeginEditing = function() {
        this.setCache();
        this.streamEditing(true);
    };

    Sensor.prototype.streamCancelEditing = function() {
        this.restoreCache();
        this.streamEditing(false);
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
            this.last_calibration().coefficients = vars.last_calibration.coefficients;
            this.lastCalibration(new Date(vars.last_calibration.timestamp*1000).toDateString());
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
        if (vars.hasOwnProperty('sensor_IOtype'))
            this.isInput(vars.sensor_IOtype);
        if (vars.hasOwnProperty('last_value') && vars.last_value != "")
            this.command_value(JSON.parse(vars.last_value));

        if (vars.hasOwnProperty('datastream')){
            if(vars.datastream !== null){
                this.streamName(vars.datastream.name);
                this.streamDescription(vars.datastream.description);
                this.streamUuid(vars.datastream.id);
                this.paths(vars.datastream.paths);
            }
        }

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

    Sensor.prototype.checkPaths = function(){

        var counter = 0;
        var foundPaths = false;
         while(!foundPaths){
            newpath = $("#newpaths_" + counter);
            if(newpath.length > 0){
                if(newpath[0].value[0] != "/"){
                    return false;
                }
                if(newpath[0].value[newpath[0].value.length-1] == "/"){
                    return false;
                }
                counter++;
            } else {
                foundPaths = true;
            }
        }
        return true;
    };



    Sensor.prototype.DisplayWarning = function(msg, location){
        //TODO use location to display errors on different parts of the page
        var __this = this;
        __this.errorMessage(msg);
    };

    Sensor.prototype.streamToDict = function() {
        data = {
            'name': this.streamName(),
            'description': this.streamDescription(),
            'paths': []
        };
        var foundPaths = false;
        var counter = 0;
        while(!foundPaths){
            newpath = $("#newpaths_" + counter);
            if(newpath.length > 0){
                data.paths.push(newpath[0].value);
                counter++;
                if(counter > 5){
                    foundPaths = true;
                }
            } else {
                foundPaths = true;
            }
        }
        return data;
    };
