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

$(function() {
    "use strict";

    function GraphWidget(vars) {
        var __this = this;

        var deafultOptions = {
            xaxis: {
                  mode:       'time'
                 ,timeformat: '%m-%d %I:%M %P'
                 ,timezone:   'browser'
            }

            ,crosshair: { mode: 'x'}
            ,selection: { mode: 'x'}

            ,grid: {
                 autoHighlight: false
                ,hoverable:     true
                ,clickable:     true
            }
        };

        var graphEle = null;
        var graphEleOverview = null;

        var graphOptions = $.extend(true, {}, deafultOptions);
        var graphOverviewOptions = $.extend(true, {yaxis: {show: false}}, deafultOptions);

        this.plot = ko.observable(null);
        this.plotOverview = ko.observable(null);

        this.selectedPoints = ko.observableArray();
        this.locked = ko.observable(false);

        this.units = null;

        this.graphData = ko.observableArray();
        this.graphOverviewData = ko.observableArray();

        this.noData = ko.computed(function() {
            return (__this.graphData().length <= 0 && __this.graphOverviewData().length <= 0) ? true : false;
        });

        this.isZoomed = ko.observable(false);
        this.zoomed = function() {
            var graphX = {};
            var overviewX = {};

            if (this.plot() === null || this.plotOverview() === null) {
                if (!graphOptions.hasOwnProperty('xaxis') || !graphOverviewOptions.hasOwnProperty('xaxis'))
                    return false;

                graphX = graphOptions.xaxis;
                overviewX = graphOverviewOptions.xaxis;
            }
            else {
                graphX = this.plot().getAxes().xaxis;
                overviewX = this.plotOverview().getAxes().xaxis;
            }

            if (graphX.min === overviewX.min && graphX.max === overviewX.max)
                return false;

            return true;
        };

        this.graphRange = function() {
            if (this.plot() === null)
                return null;

            var graphX = this.plot().getAxes().xaxis;
            return {start: graphX.min, end: graphX.max};
        };


        this.options         = function() { return graphOptions; };
        this.overviewOptions = function() { return graphOverviewOptions; };

        this.graphStart = function(epoch) {
            graphOptions['xaxis']['min'] = epoch ? epoch * 1000 : null;
            graphOverviewOptions['xaxis']['min'] = epoch ? epoch * 1000 : null;
            if (this.plotOverview())
                this.plotOverview().clearSelection();
        };

        this.graphEnd = function(epoch) {
            graphOptions['xaxis']['max'] = epoch ? epoch * 1000 : null;
            graphOverviewOptions['xaxis']['max'] = epoch ? epoch * 1000 : null;
            if (this.plotOverview())
                this.plotOverview().clearSelection();
        };

        this.resetZoom = function() {
            this.plotOverview().clearSelection();
            this.graphData(this.graphOverviewData());
            graphOptions['xaxis']['min'] = graphOverviewOptions['xaxis']['min'];
            graphOptions['xaxis']['max'] = graphOverviewOptions['xaxis']['max'];
            this.drawGraph();
            $(this).trigger("zoomreset");
        };

        this.zoomGraph = function(range) {
            if (!range.hasOwnProperty('start') || !range.hasOwnProperty('end'))
                return null;

            var start = range['start'];
            var end   = range['end'];

            if (start > end)
                return null;

            graphOptions['xaxis']['min'] = start * 1000;
            graphOptions['xaxis']['max'] = end * 1000;
            return range;
        };

        this.rebuild = function(vars) {
            vars = vars || {};

            if (vars.hasOwnProperty('units'))
                __this.units = vars.units;
        };

        var init = function(vars) {
            vars = vars || {};

            graphEle = $("#graph").get(0);
            graphEleOverview = $("#graph-overview").get(0);

            __this.rebuild(vars);
        };

        var plotHoverHandler = function(e, pos, item) {
            if (__this.locked())
                return;

            var axes = __this.plot().getAxes();
            if (pos.x < axes.xaxis.min || pos.x > axes.xaxis.max ||
                pos.y < axes.yaxis.min || pos.y > axes.yaxis.max) {
                return;
            }

            var pos1 = null, pos2 = null;
            var pos1Index = null, pos2Index = null;
            var i, j, dataset = __this.plot().getData();
            for (i = 0; i < dataset.length; ++i) {
                var series = dataset[i];
                for (j = 0; j < series.data.length; ++j) {
                    if(series.data[j] === null)
                        continue;
                    if (series.data[j][0] > pos.x) {
                        pos2 = series.data[j];
                        pos2Index = j;
                        break;
                    }
                    else {
                        pos1 = series.data[j];
                        pos1Index = j;
                    }
                }
                break;
            }

            //Don't care if theres no data
            if(pos1 === null && pos2 === null)
                return;

            //Base cases of either pos1 or pos2 being null in which case the other non null value
            //automatically gets selected.  Otherwise we compare the difference between the pos1/pos2 and
            //the position of the mouse and see which ones smaller.
            var selected = null;
            var selectedIndex = null;
            if(pos1 === null && pos2 !== null) {
                __this.plot().lockCrosshair({'x': pos2[0]});
                selected = pos2;
                selectedIndex = pos2Index;
            }
            else if(pos1 !== null && pos2 === null) {
                __this.plot().lockCrosshair({'x': pos1[0]});
                selected = pos1;
                selectedIndex = pos1Index;
            }
            else if(Math.abs(pos1[0] - pos.x) <= Math.abs(pos2[0] - pos.x)) {
                __this.plot().lockCrosshair({'x': pos1[0]});
                selected = pos1;
                selectedIndex = pos1Index;
            }
            else {
                __this.plot().lockCrosshair({'x': pos2[0]});
                selected = pos2;
                selectedIndex = pos2Index;
            }

            __this.plot().unhighlight();
            __this.plot().highlight(0, selectedIndex);
            var dp = dataset[0].data[selectedIndex];
            var dpInfo = {
                 series: 0
                ,color:  dataset[0].color
                ,point:  dp
                ,label:  dp[1].toFixed(2) + " at " + formatDate(new Date(dp[0]), true)
            };

            $("#graph-tooltip").find('span').html(dpInfo.label);
            var toolWidth = $("#graph-tooltip").width();
            var left = toolWidth+pos.pageX+25+10 >= $(window).width() ? pos.pageX-toolWidth-25 : pos.pageX+25;
            $("#graph-tooltip").css({top: pos.pageY, left: left}).fadeIn(200);

            updateSelectedPoints(dpInfo, 'series');
        };

        var plotMouseoutHandler = function() {
            if (__this.locked())
                return;

            __this.clearPlotSelections();
        };

        var plotSelectedHandler = function(e, ranges) {
            var start = ranges.xaxis.from;
            var end   = ranges.xaxis.to;

            var range = {start: Math.round(start/1000), end: Math.round(end/1000)};

            __this.clearPlotSelections();
            __this.plotOverview().setSelection({xaxis: {from: start, to: end}}, true);
            __this.zoomGraph(range);

            $(__this).trigger('zoomed', range);
        };

        var plotClickHandler = function(e, pos, item) {
            __this.locked(!__this.locked());
        };

        var updateSelectedPoints = function(dpInfo, key) {
            var updated = false;

            $.each(__this.selectedPoints(), function(i, dp) {
                var hasKey = dp().hasOwnProperty(key) && dpInfo.hasOwnProperty(key);

                if (hasKey && dp()[key] == dpInfo[key]) {
                    dp(dpInfo);
                    updated = true;
                }
            });

            if (!updated)
                __this.selectedPoints.push(ko.observable(dpInfo));
        };

        this.graphEle = function() { return graphEle; };
        this.graphEleOverview = function() { return graphEleOverview; };

        this.addPlotHandlers = function() {
            $(this.graphEle()).on("plothover", plotHoverHandler);
            $(this.graphEle()).on("mouseout", plotMouseoutHandler);
            $(this.graphEle()).on("plotclick", plotClickHandler);
            $(this.graphEle()).on("plotselected", plotSelectedHandler);

            $(this.graphEleOverview()).on("mouseout", plotMouseoutHandler);
            $(this.graphEleOverview()).on("plothover", plotHoverHandler);
            $(this.graphEleOverview()).on("plotselected", plotSelectedHandler);
        };

        init(vars);
    };  // End GraphWidget

    GraphWidget.prototype.clearPlotSelections = function() {
        if (this.plot() !== null) {
            this.plot().clearSelection();
            this.plot().clearCrosshair();
            this.plot().unhighlight();
        }

        this.selectedPoints.removeAll();
        $('#graph-tooltip').hide();
    };

    GraphWidget.prototype.drawGraph = function() {
        this.clearPlotSelections();

        if (!this.noData()) {
            $(this.graphEle()).show();
            $(this.graphEleOverview()).show();

            this.locked(false);

            if (this.plot() === null) {
                var yAxisLabel = $("<div class='yaxis-label'></div>").text(this.units);

                var data = this.graphData();
                var overviewData = this.graphOverviewData();

                var options = this.options();
                var overviewOptions = this.overviewOptions();

                this.plot($.plot(this.graphEle(), [data], options));
                this.plotOverview($.plot(this.graphEleOverview(), [overviewData], overviewOptions));

                $(this.graphEle()).append(yAxisLabel);
                this.addPlotHandlers();

                if (this.zoomed()) {
                    this.isZoomed(true);
                    var zoomRange = this.graphRange();
                    this.plotOverview().setSelection({xaxis: {from: zoomRange['start'], to: zoomRange['end']}}, true);
                }
                else
                    this.isZoomed(false);

            }
            else {
                var options = this.options();
                var overviewOptions = this.overviewOptions();

                this.plot().setData([this.graphData()]);
                this.plotOverview().setData([this.graphOverviewData()]);

                this.plot().getOptions().xaxes[0].min = options.xaxis.min;
                this.plot().getOptions().xaxes[0].max = options.xaxis.max;
                this.plotOverview().getOptions().xaxes[0].min = overviewOptions.xaxis.min;
                this.plotOverview().getOptions().xaxes[0].max = overviewOptions.xaxis.max;

                this.plot().setupGrid();
                this.plotOverview().setupGrid();

                if (this.zoomed())
                    this.isZoomed(true);
                else
                    this.isZoomed(false);

                this.plot().draw();
                this.plotOverview().draw();
            }
        }
        else {
            $(this.graphEle()).hide();
            $(this.graphEleOverview()).hide();
            this.isZoomed(false);
        }
    };

    var formatDate = function(dateObj, timeFirst) {
        //Format: mm/dd/yyyy hh:mm AM/PM  zero padded
        //hh:mm AM/PM, mm/dd/yyyy if timeFirst true

        var rawMonth =      dateObj.getMonth()+1;
        var month =         rawMonth < 10 ? "0"+rawMonth : rawMonth;
        var date =          dateObj.getDate() < 10 ? "0"+dateObj.getDate() : dateObj.getDate();
        var year =          dateObj.getFullYear();
        var rawHours =      dateObj.getHours();
        var meridianHours = rawHours % 12 == 0 ? 12 : rawHours % 12;
        var hours =         meridianHours < 10 ? "0"+meridianHours : meridianHours;
        var minutes =       dateObj.getMinutes() < 10 ? "0"+dateObj.getMinutes() : dateObj.getMinutes();
        var amPm =          rawHours >= 12 ? "PM" : "AM";

        var dStr = month+"/"+date+"/"+year;
        var tStr = hours+":"+minutes+" "+amPm;
        var dtStr = dStr + " " + tStr;

        if (timeFirst === true)
            dtStr = tStr + ", " + dStr;

        return dtStr;
    };

    window.GraphWidget = GraphWidget;
}(jQuery));
