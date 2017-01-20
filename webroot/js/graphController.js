 'use strict';

angular.module('teleceptor.graphcontroller', [])

.controller('graphController', ['$scope', '$location', '$timeout', function($scope, $location, $timeout){
    $timeout(function(){
        $location.search('reload', parseInt(Date.now()/1000));
    }, 1000);
}])

.directive('graph', ['$location', '$window', '$http', 'timeService', 'infoService', 'apiService', function($location, $window, $http, timeService, infoService, apiService){
    return{
        restrict: 'E',
        link: function(scope, elem, attrs){
            var d3 = $window.d3;

            scope.$on('$routeUpdate', function(){
                GetData();
            });
            scope.$watch(function(){
                return infoService.getStreamInfo();
            }, function(){
                GetData();
            });

            function GetData(){
                if($location.search().ds === undefined) return;
                if(infoService.getStreamInfo() === undefined ) return;

                var start, end;
                if(elem[0].clientHeight < 100){
                    start = Date.now() - 84000000;
                    end = Date.now();
                } else {
                    start = timeService.getValues().start;
                    end = timeService.getValues().end;
                    if(isNaN(start)){
                        start = Date.now() - 84000000;
                        timeService.setStart(start);
                    }
                    if(isNaN(end)){
                        end = Date.now();
                        timeService.setEnd(end);
                    }
                }
                console.log(infoService.getStreamInfo())
                apiService.get("sensors?sensor_id="+infoService.getStreamInfo().sensor).then(function(sensorInfoResponse){
                    if(elem[0].clientHeight < 100){
                        infoService.setSensorInfo(sensorInfoResponse.data.sensor);
                    }
                    var readingsUrl = "readings?datastream=" + infoService.getStreamInfo().id + "&start="+parseInt(start/1000)+"&end="+parseInt(end/1000);
                    apiService.get(readingsUrl).then(function(readingsResponse){
                        drawGraph(elem[0], readingsResponse.data);
                    }, function(error){
                        console.log("error occured: " + error);
                    });
                }, function(error){
                    console.log("error occured: " + error);
                });
            }

            function drawGraph(parent, data){
                var sensorInfo = infoService.getStreamInfo();
                scope.graphName = sensorInfo.name;
                parent.innerHTML = "";
                var width = elem[0].clientWidth;
                var height = elem[0].clientHeight;
                var additionalMargin = 0;

                var margin = {top: 20, right: 10, bottom: 20, left: 40+additionalMargin};
                if(height < 100) margin.bottom = 5;
                width = width - margin.left - margin.right; height = height - margin.top - margin.bottom;

                var newChart = d3.select(parent)
                    .append("svg")
                    .attr("class", "Chart-Container")
                    .attr("id", sensorInfo.name)
                    .attr("width", width + margin.left + margin.right)
                    .attr("height", height + margin.top + margin.bottom)
                    .append("g")
                    .attr("transform", "translate(" + margin.left + "," + 0 + ")")
                    .classed("svg-content-responsive", true);

                if(data.readings.length === 0){
                    newChart.append("g").append("text")
                        .text("No data exists for this time range.")
                        .attr("class", "ChartTitle-Text")
                        .attr("x", margin.left)
                        .attr("y", height/2);
                    return;
                }

                var start = timeService.getValues().start;
                var end = timeService.getValues().end;

                var min = data.readings[0][1];
                var max = data.readings[0][1];

                //set min and max values
                for(var j = 0; j < data.readings.length; j++){
                    if(min > data.readings[j][1]) min = data.readings[j][1];
                    if(max < data.readings[j][1]) max = data.readings[j][1];
                }

                scope.newGraph = {};
                scope.newGraph.warning = "";

                 var xScale = d3.scaleTime()
                    .domain([new Date(start), new Date(end)])
                    .rangeRound([0, width]);

                var yScale = d3.scaleLinear()
                    .domain([min,max+(max-min)*0.1])
                    .rangeRound([height,margin.bottom]);

                //y axis
                if(height > 100){
                    var yAxis = d3.axisLeft(yScale)
                        .tickSizeInner(-width)
                        .tickSizeOuter(-10)
                        .tickValues(getTic())
                        .tickFormat(function(d){
                            var whatToReturn = getFormattedText(d);
                            return getFormattedText(d);
                        });
                    newChart.append("g")
                        .attr("class", "ChartAxis-Shape")
                        .call(yAxis);
                } else {
                    var littleY = d3.axisLeft(yScale).ticks(0).tickSizeOuter(-10);
                    newChart.append("g")
                        .attr("class", "ChartAxis-Shape")
                        .call(littleY);
                }

                //X Axis
                var xAxis = d3.axisBottom(xScale)
                    .tickSizeInner(-height + margin.bottom )
                    .tickSizeOuter(0)
                    .tickPadding(10)
                    .ticks(12);

                newChart.append("g")
                    .attr("class", "ChartAxis-Shape")
                    .attr("transform", "translate(0," + height + ")")
                    .call(xAxis);


                var xAxisTop = d3.axisBottom(xScale)
                    .ticks(0);

                newChart.append("g")
                    .attr("class", "ChartAxis-Shape")
                    .attr("transform", "translate(0, "+margin.bottom+")")
                    .call(xAxisTop);

                var yAxisRight = d3.axisLeft(yScale)
                    .ticks(0);

                newChart.append("g")
                    .attr("class", "ChartAxis-Shape")
                    .attr("transform", "translate("+width+", 0)")
                    .call(yAxisRight);

                function getTic(){
                    var Ticks = [];
                    var ratio  = (max-min) / 6;
                    for(var i = 0; i < 7; i++){
                        Ticks.push(min+(ratio*i));
                    }
                    return Ticks;
                }

                var lastPos =[];
                var lastWidth = [];

                /* Graph lines
                * First gets a preliminary date, then itterates through the data keeping track of the last date.
                * Checks to see if the current date - last date is == to the average date.
                * If it isn't, create a break in the line and reset all of the values until a new date is found.
                */

                var meanTimes = [];
                var lastPoint =(data.readings[0][0]);

                for(var j = 0; j < data.readings.length; j++){
                    meanTimes.push((data.readings[j][0] - lastPoint) * 0.0001);
                    lastPoint = data.readings[j][0];
                }

                meanTimes.sort();
                var meanTime = meanTimes[meanTimes.length/2];
                var last = 0;

                var lineFunction = d3.line()
                    .defined(function(d) {

                        d[0] = parseInt(d[0]);
                        if(d[0] < start/1000 || d[0] > end/1000) return false;
                        if(d[1] > max || d[1] < min){
                            scope.newGraph.warning = "Warning: Some data points are not shown in graph and may be causing line breaks.";
                            return false;
                        }

                        var val = (d[0] - last) *0.0001;
                        if(val > meanTime*1.5 ||val < meanTime*0.5){
                            last = d[0];
                            return false;
                        }
                        last = d[0];
                        return true;
                    })
                    .x(function(d) {
                        return xScale(d[0]*1000);
                      })
                    .y(function(d) {
                        return yScale(d[1]);
                    });
                var lineGraph = newChart.append("path")
                    .attr("d", lineFunction(data.readings))
                    .attr("stroke", "#FFB90F")
                    .attr("stroke-width", 2)
                    .attr("fill", "none");

                //TOOL-TIPS
                //Tooltip container
                var tooltip = newChart.append("g")
                    .style("display", "none");

                var circleElements = [], lineElements = [], textElements = [];

                //for every stream. create a circle, text, and horizontal line element and store in an array
                var newCircle = tooltip.append("circle")
                    .attr("class", "tooltip-circle")
                    .style("fill", "none")
                    .style("stroke", "blue")
                    .attr("r", 4);
                circleElements.push(newCircle);

                var newText = tooltip.append("text")
                    .attr("width", 100*2)
                    .attr("height", 100*0.4)
                    .attr("fill", "black");

                textElements.push(newText);


                //Y-axis line for tooltip
                var yLine = tooltip.append("g")
                    .append("line")
                    .attr("class", "tooltip-line")
                    .style("stroke", "blue")
                    .style("stroke-dasharray", "3,3")
                    .style("opacity", 0.5)
                    .attr("y1", margin.bottom)
                    .attr("y2", height);

               //Date text
                var timeText = tooltip.append("text")
                    .attr("x", 0)
                    .attr("y", margin.bottom-5)
                    .attr("width", 100)
                    .attr("height", 100*0.4)
                    .attr("fill", "black");

                var myData = [];
                for(var x in data.readings){
                    myData.push(new Date(data.readings[x][0]).getTime()*1000);
                }

                //Selection box
                var selectionBox = newChart.append("rect")
                    .attr("fill", "none")
                    .attr("opacity", 0.5)
                    .attr("x",0)
                    .attr("y", margin.bottom)
                    .attr("width", 14)
                    .attr("height", height-margin.bottom)
                    .attr("class", "myselection");

                //Drag behaivors for the selection box.
                var dragStart = 0, dragStartPos = 0, dragEnd = 0;
                var drag = d3.drag()
                    .on("drag", function(d,i) {
                        var x0 = xScale.invert(d3.mouse(this)[0]).getTime(),
                            i = d3.bisect(myData, x0),
                            d0 = data.readings[i - 1],
                            d1 = data.readings[i];
                        if(d1 === undefined) return;
                        var d = x0 - d0[0]*1000 > d1[0]*1000 - x0 ? d1 : d0;
                        if(xScale(d[0]*1000) > dragStartPos){
                            selectionBox.attr("width", (xScale(d[0]*1000) - dragStartPos));
                        } else {
                            selectionBox.attr("width", ( dragStartPos - xScale(d[0]*1000)));
                            selectionBox.attr("transform", "translate(" + xScale(d[0]*1000) + ",0)" );
                        }
                    })
                    .on("end", function(d,i){
                        dragEnd = d3.mouse(this)[0];
                        if(Math.abs(dragStart - dragEnd) < 10) return;

                        var x0 = xScale.invert(dragStart), x1 = xScale.invert(dragEnd);
                        if(x1 > x0){
                            start = x0.getTime();
                            end = x1.getTime();
                        } else {
                            start = x1.getTime();
                            end = x0.getTime();
                        }

                        scope.$apply(function(){
                            $location.search('startTime', start);
                            $location.search('endTime', end);
                        });
                        timeService.setStart(start);
                        timeService.setEnd(end);
                    });
                //Hit area for selection box
                var circleHit = newChart.append("rect")
                    .attr("width", width)
                    .attr("height", height)
                    .style("fill", "none")
                    .style("pointer-events", "all")
                    .on("mouseover", function() {
                        tooltip.style("display", null);
                    })
                    .on("mouseout", function() {
                        tooltip.style("display", "none");
                    })
                    .on("mousemove", mousemove)
                    .on("mousedown", function(){
                        selectionBox.attr("fill", "#b7ff64");
                        dragStart = d3.mouse(this)[0];

                        var x0 = xScale.invert(d3.mouse(this)[0]).getTime(),
                        i = d3.bisect(myData, x0),
                        d0 = data.readings[i - 1],
                        d1 = data.readings[i];
                    if(d1 === undefined) return;
                    var d = x0 - d0[0]*1000 > d1[0]*1000 - x0 ? d1 : d0;
                        selectionBox.attr("transform", "translate(" + xScale(d[0]*1000) + ",0)" );
                        dragStartPos = xScale(d[0]*1000);
                    })
                    .call(drag);

                //Tooltip helper
                var bisectDate = d3.bisector(function(d) {
                    return d.date;
                }).left;

                function mousemove() {
                    var x0 = xScale.invert(d3.mouse(this)[0]).getTime(),
                        i = d3.bisect(myData, x0),
                        d0 = data.readings[i - 1],
                        d1 = data.readings[i];
                    var d;
                    if(d0 === undefined && d1 === undefined) return;
                    if(d0 === undefined){
                        d = d1;
                    } else if(d1 === undefined){
                        d = d0;
                    } else {
                        if(x0 -d0[0]*1000 > d1[0]*1000 -x0){
                            d = d1;
                        } else {
                            d = d0;
                        }
                    }
                    circleElements[0].attr("transform", "translate(" + xScale(d[0]*1000) + "," + yScale(d[1]) + ")");
                    yLine.attr("transform", "translate(" + xScale(d[0]*1000) + "," + 0 + ")");
                    if(height > 100)
                        timeText.text(new Date(d[0]*1000));

                    textElements[0]
                        .text(getFormattedText(d[1]))
                        .attr("transform", "translate(" + (xScale(d[0]*1000)+10) + "," + (yScale(d[1])-10) + ")");

                }

                 //Formats text
                function getFormattedText(d){
                    var f = d3.format(".1f");
                    var count = Math.round(d).toString().length;
                    f = d3.format(".2f");
                    var info = infoService.getSensorInfo();
                    if(info.units === null) return f(d);
                    if(sensorInfo.units === "$") return sensorInfo.units + f(d);
                    return f(d) + sensorInfo.units;
                 }
            }
        }
    };
}]);