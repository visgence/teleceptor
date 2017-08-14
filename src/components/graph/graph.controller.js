import * as d3 from 'd3';

export default class graphController {
    constructor(infoService, apiService, $location, $scope, $timeout, $window) {
        'ngInject';
        this.$location = $location;
        this.$scope = $scope;
        this.$timeout = $timeout;
        this.infoService = infoService;
        this.apiService = apiService;

        // watch window resize
        angular.element($window).bind('resize', () => {
            if ($location.search().datastream !== undefined) {
                this.drawGraph(infoService.getReadings());
            }
        });

        // Wait until sensor info is loaded to get reading data.
        this.$scope.$watch(() => this.infoService.getSensor(), (nv, ov) => {
            if (nv === undefined) {
                return;
            }
            if (nv === ov) {
                return;
            }
            $scope.title = nv.name;
            this.getData();
        });

        // If no datastream is selected, warn user.
        if ($location.search().datastream === undefined) {
            $scope.title = 'Please select a datastream.';
            $('#graph-container').css('height', 0);
        }
    }

    // Makes a call to the readings api endpoint to get graph data.
    getData() {
        const url = 'readings/?' + location.href.split('?')[1];
        this.apiService.get(url)
            .then((success) => {
                if (success.data.error !== undefined) {
                    $('#graph-message').toggleClass('graph-message-display');
                    $('#graph-message').html('<h3>No data could be found.</h3>');
                } else {
                    this.drawGraph(success.data);
                    this.infoService.setReadings(success.data);
                }
            })
            .catch((error) => {
                console.log('error');
                console.log(error);
            });
    }

    // D3 drawing.
    drawGraph(data) {
        // If no data points were returned, warn the user and quit.
        if (data.readings.length === 0) {
            $('#graph-message').toggleClass('alert-danger');
            $('#graph-message').toggleClass('graph-message-display');
            $('#graph-message').html('<h3>Not enough points were returned.</h3>');
            return;
        }
        let width = $('#graph-container')[0].clientWidth;
        let height = 350;

        // Make sure the previous graph is deleted.
        $('#graph-container').empty();

        // Scale all of the readings by their coefficients and translate unix time to milliseconds
        let coefs = this.infoService.getSensor().last_calibration.coefficients;
        if (coefs.constructor !== Array) {
            coefs = coefs.split(',');
        }
        const scaledReadings = [];
        data.readings.forEach((reading) => {
            const newReading = [reading[0] * 1000, reading[1] * parseFloat(coefs[0]) + parseFloat(coefs[1])];
            scaledReadings.push(newReading);
        });
        data.readings = scaledReadings;

        // Find the limits of the graph.
        let min = data.readings[0][1];
        let max = data.readings[0][1];
        let oldest = data.readings[0][0];
        let latest = data.readings[0][0];
        let j = 0;
        for (j = 0; j < data.readings.length; j++) {
            if (min > data.readings[j][1]) {
                min = data.readings[j][1];
            }
            if (max < data.readings[j][1]) {
                max = data.readings[j][1];
            }
            if (oldest < data.readings[j][0]) {
                oldest = data.readings[j][0];
            }
            if (latest > data.readings[j][0]) {
                latest = data.readings[j][0];
            }
        }

        // Add Y-axis padding if min = max.
        if (min === max) {
            const offset = min * 0.01;
            min = min > 0 ? min - offset : min + offset;
            max = max > 0 ? max + offset : max - offset;
        }

        // Set graph time range.
        let start = new Date().getTime() - 60 * 60 * 6 * 1000;
        let end = new Date().getTime();

        if (this.$location.search().start !== undefined) {
            start = parseInt(this.$location.search().start * 1000);
        }
        if (this.$location.search().end !== undefined) {
            end = parseInt(this.$location.search().end * 1000);
        }

        // Make sure all points returned are within the calculated time range
        // Note: This should never occur, left in as a sanity check.
        if (latest < start || oldest > end) {
            $('#graph-message').toggleClass('alert-danger');
            $('#graph-message').toggleClass('graph-message-display');
            $('#graph-message').html('<h3>Not enough points were returned.</h3>');
            return;
        }

        // Used to calculate the left margin.
        const unitSize = ' ' + this.FormatText(max).length;

        const margin = {
            top: 20,
            right: 10,
            bottom: 20,
            left: 10 + (unitSize * 7),
        };
        width = width - margin.left - margin.right;
        height = height - margin.top - margin.bottom;

        // Create the svg and attach it to its container
        const newChart = d3.select('#graph-container')
            .append('svg')
            .attr('class', 'Chart-Container')
            .attr('width', width + margin.left + margin.right)
            .attr('height', height + margin.top + margin.bottom)
            .append('g')
            .attr('transform', 'translate(' + margin.left + ',' + 0 + ')')
            .classed('svg-content-responsive', true);
        this.chart = newChart;

        // Calculate where in screen position X should a point be.
        const xScale = d3.scaleTime()
            .domain([
                new Date(start),
                new Date(end),
            ])
            .rangeRound([
                0,
                width,
            ]);

        // Calculate where in screen position Y should a point be.
        const yScale = d3.scaleLinear()
            .domain([
                min - (max - min) * 0.1,
                max + (max - min) * 0.1,
            ])
            .rangeRound([
                height,
                margin.bottom,
            ]);

        // Define the values of tics on the y axis.
        function getTic() {
            const Ticks = [];
            const ratio = (max - min) / 6;
            for (let i = 0; i < 7; i++) {
                Ticks.push(min + (ratio * i));
            }
            return Ticks;
        }

        // Create the bottom X axis.
        const xAxis = d3.axisBottom(xScale)
            .tickSizeInner(-height + margin.bottom)
            .tickSizeOuter(0)
            .tickPadding(10)
            .ticks(12);

        newChart.append('g')
            .attr('class', 'chart-axis')
            .attr('transform', 'translate(0,' + height + ')')
            .call(xAxis);

        // Create the left Y axis.
        const yAxis = d3.axisLeft(yScale)
            .tickSizeInner(-width)
            .tickSizeOuter(-10)
            .tickValues(getTic())
            .tickFormat((d) => {
                return this.FormatText(d);
            });

        newChart.append('g')
            .attr('class', 'chart-axis')
            .call(yAxis);

        // Create the top X axis.
        const xAxisTop = d3.axisBottom(xScale)
            .ticks(0);

        newChart.append('g')
            .attr('class', 'chart-axis')
            .attr('transform', 'translate(0, ' + margin.bottom + ')')
            .call(xAxisTop);

        // Create the right Y axis.
        const yAxisRight = d3.axisLeft(yScale)
            .ticks(0);

        newChart.append('g')
            .attr('class', 'chart-axis')
            .attr('transform', 'translate(' + width + ', 0)')
            .call(yAxisRight);


        // Generate an array of differences between two sequential dates.
        const medianTimes = [];
        let lastPoint = (data.readings[0][0]);

        for (j = 0; j < data.readings.length; j++) {
            medianTimes.push((data.readings[j][0] - lastPoint) * 0.0001);
            lastPoint = data.readings[j][0];
        }
        // Sort the array and take the median difference.
        medianTimes.sort();
        const medianTime = medianTimes[parseInt(medianTimes.length / 2)];
        let last;

        // The function used to generate the connections between points.
        const lineFunction = d3.line()
            .defined((d) => {
                // If there are less than three points, we draw the connections always.
                if (data.readings.length < 3) {
                    return true;
                }
                // If the point falls outside of graph time range, we don't draw it.
                if (d[0] < start || d[0] > end) {
                    return false;
                }
                // If a point falls outside of y axis range, we don't draw it and give a warning.
                if (d[1] > max || d[1] < min) {
                    scope.newGraph.warning = 'Warning: Some data points are not shown in graph and may be causing line breaks.';
                    return false;
                }

                if (last === null) {
                    last = d[0];
                    return true;
                }

                // If too much time has elapsed between this point and the last, we create a break.
                const val = (d[0] - last) * 0.0001;
                if (val > medianTime * 1.5 || val < medianTime * 0.5) {
                    last = d[0];
                    return false;
                }
                last = d[0];
                return true;
            })
            // Find x position of a point.
            .x((d) => {
                return isNaN(xScale(d[0])) ? 0 : xScale(d[0]);
            })
            // Find y position of a point.
            .y((d) => {
                return yScale(d[1]);
            });
        newChart.append('path')
            .attr('d', lineFunction(data.readings))
            .attr('stroke', '#FFB90F')
            .attr('stroke-width', 2)
            .attr('fill', 'none');


        // Create a container to store all the tool tip components.
        const tooltip = newChart.append('g')
            .style('display', 'none');

        // Create a point on the line where the mouse is over.
        const toolTipCircle = tooltip.append('circle')
            .attr('class', 'tooltip-circle')
            .style('fill', 'none')
            .style('stroke', 'blue')
            .attr('r', 4);

        // Add text to display the current value.
        const toolTipText = tooltip.append('text')
            .attr('width', 100 * 2)
            .attr('height', 100 * 0.4)
            .attr('fill', 'black');

        // Y-axis line for tooltip
        const yLine = tooltip.append('g')
            .append('line')
            .attr('class', 'tooltip-line')
            .style('stroke', 'blue')
            .style('stroke-dasharray', '3,3')
            .style('opacity', 0.5)
            .attr('y1', margin.bottom)
            .attr('y2', height);

        // Add the full date and value of the hovered over point.
        const timeText = tooltip.append('text')
            .attr('x', 0)
            .attr('y', margin.bottom - 5)
            .attr('width', 100)
            .attr('height', 100 * 0.4)
            .attr('fill', 'black');

        // Selection box
        const selectionBox = newChart.append('rect')
            .attr('fill', 'none')
            .attr('opacity', 0.5)
            .attr('x', 0)
            .attr('y', margin.bottom)
            .attr('width', 14)
            .attr('height', height - margin.bottom)
            .attr('class', 'myselection');

        const myData = [];
        data.readings.forEach((reading) => {
            myData.push(new Date(reading[0]).getTime());
        });

        // Drag behaivors for the selection box.
        let dragStart = 0;
        let dragStartPos = 0;
        let dragEnd = 0;
        const drag = d3.drag()
            .on('drag', (d, i) => {
                const x0 = xScale.invert(d3.event.x).getTime();

                i = d3.bisect(myData, x0);
                const d0 = data.readings[i - 1];
                const d1 = data.readings[i];
                if (d1 === undefined) {
                    return;
                }
                d = x0 - d0[0] > d1[0] - x0 ? d1 : d0;
                if (xScale(d[0]) > dragStartPos) {
                    selectionBox.attr('width', (xScale(d[0]) - dragStartPos));
                } else {
                    selectionBox.attr('width', (dragStartPos - xScale(d[0])));
                    selectionBox.attr('transform', 'translate(' + xScale(d[0]) + ',0)');
                }
            })
            .on('end', () => {
                dragEnd = d3.event.x;
                if (Math.abs(dragStart - dragEnd) < 10) {
                    return;
                }

                const x0 = xScale.invert(dragStart);
                const x1 = xScale.invert(dragEnd);
                if (x1 > x0) {
                    start = x0.getTime();
                    end = x1.getTime();
                } else {
                    start = x1.getTime();
                    end = x0.getTime();
                }
                this.$scope.$apply(() => {
                    this.$location.search('start', parseInt(start / 1000));
                    this.$location.search('end', parseInt(end / 1000));
                });
            });
        // Creates an invisible rectangle over the graph to capture all mouse events.
        newChart.append('rect')
            .attr('width', width)
            .attr('height', height)
            .style('fill', 'none')
            .style('pointer-events', 'all')
            // Show tools tips on mouse over the graph.
            .on('mouseover', () => {
                tooltip.style('display', null);
            })
            // Hide tool tips if mouse is not over the graph.
            .on('mouseout', () => {
                tooltip.style('display', 'none');
            })
            // Any change in the mouse position over the graph, update the tool tips.
            .on('mousemove', () => {
                const x0 = xScale.invert(d3.event.offsetX - margin.left).getTime();
                const i = d3.bisect(myData, x0);
                const d0 = data.readings[i - 1];
                const d1 = data.readings[i];
                let d = 0;
                if (d0 === undefined && d1 === undefined) {
                    return;
                }
                if (d0 === undefined) {
                    d = d1;
                } else if (d1 === undefined) {
                    d = d0;
                } else {
                    if (x0 - d0[0] > d1[0] - x0) {
                        d = d1;
                    } else {
                        d = d0;
                    }
                }
                if (d[1] < min || d[1] > max) {
                    return;
                }

                toolTipCircle.attr('transform', 'translate(' + xScale(d[0]) + ',' + yScale(d[1]) + ')');
                yLine.attr('transform', 'translate(' + xScale(d[0]) + ',' + 0 + ')');
                timeText.text(new Date(d[0]) + ' | ' + this.FormatText(d[1]));

                toolTipText
                    .text(this.FormatText(d[1]))
                    .attr('transform', 'translate(' + (xScale(d[0]) + 10) + ',' + (yScale(d[1]) - 10) + ')');

            })
            // Log the start position of a drag.
            .on('mousedown', () => {
                selectionBox.attr('fill', '#b7ff64');
                dragStart = d3.event.offsetX - margin.left;

                const x0 = xScale.invert(d3.event.offsetX - margin.left).getTime();
                const i = d3.bisect(myData, x0);
                const d0 = data.readings[i - 1];
                const d1 = data.readings[i];
                if (d1 === undefined) {
                    return;
                }
                const d = x0 - d0[0] > d1[0] - x0 ? d1 : d0;
                selectionBox.attr('transform', 'translate(' + xScale(d[0]) + ',0)');
                dragStartPos = xScale(d[0]);
            })
            .call(drag);
    };

    // Formats text for units display
    FormatText(d) {
        let count = 0;
        while (Math.abs(d) >= 1000) {
            d /= 1000;
            count++;
        }
        while (Math.abs(d) < 1 && d !== 0) {
            d *= 1000;
            count--;
        }
        const f = d3.format('.2f');
        let suffix;
        switch (count) {
            case -1:
                suffix = 'm';
                break;
            case -2:
                suffix = 'u';
                break;
            case -3:
                suffix = 'p';
                break;
            case 1:
                suffix = 'K';
                break;
            case 2:
                suffix = 'M';
                break;
            case 3:
                suffix = 'G';
                break;
            default:
                suffix = '';
        }
        let formattedText = f(d) + suffix + ' ';

        const info = this.infoService.getSensor();
        if (info !== undefined && info.units !== null) {
            if (info.units === '$') {
                formattedText = '$' + formattedText;
            } else {
                formattedText = formattedText + info.units;
            }
        }
        return formattedText;
    }
}
