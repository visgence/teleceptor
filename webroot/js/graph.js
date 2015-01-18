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

    function Graph(vars) {
        var __this = this;

        var zoomRange   = null;

        //Store the promise we get from fetching graph data here so we can keep from stacking up the requests
        var dataPromise = null;
        this.dataPromise = function(newPromise) { dataPromise = newPromise; };

        //Used purely for showing/hiding the loading spinner
        this.isLoading = ko.observable(true);

        this.datastream  = ko.observable();
        this.sensor      = ko.observable();
        this.graphWidget = ko.observable();

        this.rangeStart = ko.observable();
        this.rangeEnd   = ko.observable();

        this.isZoomed = ko.computed(function() {
            var graphWidget = this.graphWidget();
            if (graphWidget)
                return graphWidget.isZoomed();
            return false;
        }, this);

        /*********************************************************************************
                                       Privilaged Methods
        **********************************************************************************/


        this.rebuild = function(vars) {
            vars = vars || {};

            this.rangeStart(vars['start'] ? vars['start'] : null);
            this.rangeEnd(vars['end'] ? vars['end'] : null);
            zoomRange = vars.zoomRange ? vars.zoomRange : {};
        };


        this.zoomRange = function() { return zoomRange; };
        this.shouldZoom = function() {
            if (zoomRange && zoomRange.hasOwnProperty('start') && zoomRange.hasOwnProperty('end'))
                return true;
            return false;
        };


        /*********************************************************************************
                                       Private Methods
        **********************************************************************************/

        var initGraphWidget = function(vars) {
            vars = vars || {};

            //Init graph widget
            var graphData = {
                 units: __this.sensor().units()
            };

            __this.graphWidget(new GraphWidget(graphData));
            $(__this.graphWidget()).on('zoomed', zoomedHandler);
            $(__this.graphWidget()).on('zoomreset', zoomResetHandler);

            //Set intial values
            __this.graphWidget().graphStart(__this.rangeStart());
            __this.graphWidget().graphEnd(__this.rangeEnd());
            __this.graphWidget().zoomGraph(zoomRange);

            __this.rebuildGraphData().then(function() {
                __this.graphWidget().drawGraph();
            });

        };

        var init = function(vars) {
            vars = vars || {};

            if (vars.hasOwnProperty("sensor"))
                __this.sensor = vars.sensor;

            if (vars.hasOwnProperty("datastream"))
                __this.datastream(vars.datastream);

            __this.rebuild(vars);

            initGraphWidget(vars);
        };


        /**************************** Event Handlers *************************************/

        var zoomResetHandler = function() {
            zoomRange = null;
            $(__this).trigger('zoomreset');
        };

        var zoomedHandler = function(e, newZoomRange) {
            zoomRange = null;
            $(__this).trigger('zoomed', newZoomRange);
            zoomRange = newZoomRange;
            __this.fetchForZoom();
        };

        var setEpochHandler = function(epoch) {
            if (typeof(epoch) == "number") {
                $(this).datetimepicker('update', new Date(epoch * 1000));
                $(this).trigger('change');
            }
        }

        init(vars);
    };  //END GRAPH


    /*********************************************************************************
                                    Public Methods
    **********************************************************************************/


    Graph.prototype.resetZoom = function() {
        this.graphWidget().resetZoom();
        $(this).triggerHandler('zoomreset');
    };


    /****************** Setters, Getters, Condition Checkers *************************/


    Graph.prototype.setRange = function(newRange) {
        this.rebuild(newRange);
        return this.fetchForRange((newRange));
    };

    Graph.prototype.getRange = function() {
        var range = {};
        if (this.rangeStart())
            range['start'] = this.rangeStart();
        if (this.rangeEnd())
            range['end'] = this.rangeEnd();

        return range;
    };

    //Fetch data for the graph using the range from the zoomRange. Make sure to leave the overview alone though.
    Graph.prototype.fetchForZoom = function() {
        var __this = this;
        if (!this.shouldZoom())
            return;

        return this.fetchData(this.zoomRange()).then(function(readings) {
            __this.graphWidget().graphData(readings);
            __this.graphWidget().drawGraph();
        });
    };


    //Fetch data for a specified range for both the graph and it's overview
    Graph.prototype.fetchForRange = function(range) {
        var __this = this;
        return this.fetchData(range).then(function(readings) {
            var readingsCopy = $.extend(true, [], readings);
            __this.graphWidget().graphData(readings);
            __this.graphWidget().graphOverviewData(readingsCopy);
            __this.graphWidget().graphStart(__this.rangeStart());
            __this.graphWidget().graphEnd(__this.rangeEnd());
            __this.graphWidget().drawGraph();
        });
    };

    //Rebuild the graph and it's overview.  If we should start the graph out zoomed it will make a seperate call
    //to fetch 'zoomed in' data otherwise it just uses the same data for both graph and overview.
    Graph.prototype.rebuildGraphData = function() {
        var __this = this;

        //First get data for the overview graph
        var overviewData = [];
        var dataPromise = this.fetchData(this.getRange()).then(function(readings) {
            __this.graphWidget().graphOverviewData(readings);
            overviewData = readings;
        });

        //If we should zoom then get seperate data for main graph otherwise just copy the data already recieved.
        dataPromise = dataPromise.then(function() {
            if (__this.shouldZoom()) {
                return __this.fetchData(__this.zoomRange()).then(function(readings) {
                    __this.graphWidget().graphData(readings);
                });
            }
            else {
                var graphData = $.extend(true, [], overviewData);
                __this.graphWidget().graphData(graphData);
            }
        });

        return dataPromise;
    };


    Graph.prototype.fetchData = function(range) {
        var __this = this;
        var dsId = this.datastream().id;

        if (!dsId)
            return $.Deferred().reject().promise();

        var url = getGraphDataUrl(dsId, range);
        var coefficients = [];
        if (this.sensor().last_calibration())
            coefficients = this.sensor().last_calibration().coefficients;

        this.isLoading(true);
        var promise = $.get(url).then(function(resp) {
            __this.isLoading(false);
            //activeSensor().command_value(resp.readings[resp.readings.length -1]);
            return scaleData(resp.readings, coefficients);
        });

        this.dataPromise(promise);
        return promise;
    };


    /*********************************************************************************
                                     Helper Methods
    **********************************************************************************/

    var scaleDataPoint = function(val, coefficients) {

        var length = coefficients.length;
        var result = 0;

        for (var i = 0; i < length; i++) {
            result += Math.pow(val, i) * coefficients[length-1-i];
        }

        return result;
    };


    var scaleData = function(data, coefficients) {

        var tmpData    = [];
        var avg_t_diff = 0;
        var t_diff     = null;
        var n_t_diff   = 0;
        var last_t     = 0;

        for(var i = 0; i < data.length; i++) {
            if (i > 0 && tmpData[tmpData.length-1]) {
                t_diff = data[i][0] - last_t;
                n_t_diff++;
                avg_t_diff = ((n_t_diff-1)*avg_t_diff + t_diff)/n_t_diff;
                if ( avg_t_diff > 0 && t_diff > 3*avg_t_diff )
                    tmpData.push(null);
            }
            last_t = data[i][0];
            var tmp = [];
            tmp[0] = data[i][0] * 1000;
            tmp[1] = scaleDataPoint(data[i][1], coefficients);

            tmpData.push(tmp);
        }

        return tmpData;
    };

    var getGraphDataUrl = function(dsId, range) {
        var url = '/api/readings/';
        var granularity = 300;

        url += "?datastream=" + dsId + "&granularity=" + granularity;

        if (range.hasOwnProperty('start') && range['start'])
            url += "&start=" + range['start']
        if (range.hasOwnProperty('end') && range['end'])
            url += "&end=" + range['end']

        return url;
    };

    window.Graph = Graph;
}(jQuery));
