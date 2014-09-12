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


$(function($) {
	"use strict";

    $("form :checkbox").bootstrapSwitch();

	function SensorsIndex(vars) {
        var __this = this;

        this.activeSensor = ko.observable();
        this.sensors = ko.observableArray();
        this.timeControls = ko.observable();
        this.graph = ko.observable();
        this.msg = ko.observable();
        this.isLoading = ko.observable(false);

        this.isActive = function(sensor) {
            return this.activeSensor() && this.activeSensor().uuid() === sensor.uuid() ? true:false;
        };

        this.activateSensor = function(sensor) {
            if (this.isActive(sensor))
            	return;

            this.activeSensor(sensor);
        };


		function init(vars) {
            vars = vars || {};

            if (vars.hasOwnProperty("activeSensor"))
                __this.activeSensor(new Sensor(vars.activeSensor));

            initTimeControls(vars);
            

            
            //TODO: Get params from url for graph init
            vars["sensor"] = vars["activeSensor"];
			initGraph(vars);

            $("#sensor-tabs").on("click", "li.tab", switchSensorTab);

            //Handle switching sensor here so we can preserve other parts of url query string
            $(".sensor-list").on("click", "a.sensor", function(e) {
                var sensorId = $(e.currentTarget).data("sensorid");
                if (sensorId)
                    $.fn.updateRoute({"sensor_id": sensorId}, true);
            });
		}

        function switchSensorTab(e) {
            var curTab = $(e.currentTarget).siblings("li.active");
            $("#"+$(curTab).data("tab")).addClass("hidden");
            $(curTab).removeClass("active");

            $(e.currentTarget).addClass("active");
            $("#"+$(e.currentTarget).data("tab")).removeClass("hidden");
        }

        function initTimeControls(params) {
            params = params || {};

            var tc = new TimeControls(params);
            __this.timeControls(tc);
            $(__this.timeControls()).on('timechanged', timeChanged.bind(__this));
            $(__this.timeControls()).on('rangechanged', timeChanged.bind(__this));
        }

        function initGraph(params) {
            params = params || {};

            var range = {
                'start': __this.timeControls().startRange.epochValue(),
                'end': __this.timeControls().endRange.epochValue()
            };

            if (range.hasOwnProperty('start') && range['start'])
                params['start'] = range['start'];
            if (range.hasOwnProperty('end') && range['end'])
                params['end'] = range['end'];

            var zoom = {};
            if (params.hasOwnProperty('startZoom'))
                zoom['start'] = params.startZoom;
            if (params.hasOwnProperty('endZoom'))
                zoom['end'] = params.endZoom;

            params['zoomRange'] = zoom;
            var graph = new Graph(params);
            __this.graph(graph);
            $(__this.graph()).on('zoomed', zoomedHandler);
            $(__this.graph()).on('zoomreset', zoomResetHandler);
            __this.graph().isLoading.subscribe(function(loading) {
                __this.timeControls().isBusy(loading);
                __this.isLoading(loading);
            });

        };

        var zoomedHandler = function(e, newZoom) {
            $.fn.updateRoute({'startZoom': newZoom['start'], 'endZoom': newZoom['end']});
        };

        var zoomResetHandler = function(e) {
            $.fn.updateRoute({'startZoom': null, 'endZoom': null});
        };

        var timeChanged = function(ev, newTime) {
            var newRange = {};
            var route = {
                 'startZoom': null
                ,'endZoom':   null
            };


            if (newTime.hasOwnProperty('start')) {
                newRange['start'] = newTime['start'];
            }
            if (newTime.hasOwnProperty('end')) {
                newRange['end'] = newTime['end'];
            }
            if (newTime.hasOwnProperty('time'))
                route['time'] = newTime['time'];

            //Let graph know of new range so it can fetch new data.
            if (!$.isEmptyObject(newRange))
                this.graph().setRange(newRange);

            //Update route for url history but don't nav to it
            $.fn.updateRoute(route);
        };

		init(vars);
	}

    window.SensorsIndex = SensorsIndex;
}(jQuery));
