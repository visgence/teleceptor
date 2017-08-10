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

        this.$scope.$watch(() => this.infoService.getSensor(), (nv, ov) => {
            if (nv === undefined) {
                return;
            }
            $scope.title = nv.name;
            this.getData();
        });
    }

    getData() {
        const datastream = this.$location.search().datastream;
        if (datastream === undefined) {
            $('#graph-message').toggleClass('graph-message-display');
            $('#graph-message').html('<h3>Please select a stream.</h3>');
            return;
        }

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

    drawGraph(data) {
        if (data.readings.length < 5) {
            $('#graph-message').toggleClass('alert-danger');
            $('#graph-message').toggleClass('graph-message-display');
            $('#graph-message').html('<h3>Not enough points were returned.</h3>');
            return;
        }
        let width = $('#graph-container')[0].clientWidth;
        let height = 350;

        $('#graph-container').empty();

        let coefs = this.infoService.getSensor().last_calibration.coefficients;
        if (coefs.constructor !== Array) {
            coefs = coefs.split(',');
        }
        const scaledReadings = [];
        data.readings.forEach((reading) => {
            const newReading = [reading[0], reading[1] * parseFloat(coefs[0]) + parseFloat(coefs[1])];
            scaledReadings.push(newReading);
        });
        data.readings = scaledReadings;

        let min = data.readings[0][1];
        let max = data.readings[0][1];
        let j = 0;
        for (j = 0; j < data.readings.length; j++) {
            if (min > data.readings[j][1]) {
                min = data.readings[j][1];
            }
            if (max < data.readings[j][1]) {
                max = data.readings[j][1];
            }
        }
        let start = new Date().getTime() - 60 * 60 * 6 * 1000;
        let end = new Date().getTime();

        console.log(start, end);

        if (this.$location.search().start !== undefined) {
            start = parseInt(this.$location.search().start * 1000);
        }
        if (this.$location.search().end !== undefined) {
            end = parseInt(this.$location.search().end * 1000);
        }

        const unitSize = ' ' + this.FormatText(max).length;

        const margin = {
            top: 20,
            right: 10,
            bottom: 20,
            left: 10 + (unitSize * 7),
        };
        width = width - margin.left - margin.right;
        height = height - margin.top - margin.bottom;

        const newChart = d3.select('#graph-container')
            .append('svg')
            .attr('class', 'Chart-Container')
            .attr('width', width + margin.left + margin.right)
            .attr('height', height + margin.top + margin.bottom)
            .append('g')
            .attr('transform', 'translate(' + margin.left + ',' + 0 + ')')
            .classed('svg-content-responsive', true);
        this.chart = newChart;

        const xScale = d3.scaleTime()
            .domain([
                new Date(start),
                new Date(end),
            ])
            .rangeRound([
                0,
                width,
            ]);

        const yScale = d3.scaleLinear()
            .domain([
                min,
                max + (max - min) * 0.1,
            ])
            .rangeRound([
                height,
                margin.bottom,
            ]);

        function getTic() {
            const Ticks = [];
            const ratio = (max - min) / 6;
            for (let i = 0; i < 7; i++) {
                Ticks.push(min + (ratio * i));
            }
            return Ticks;
        }

        // y axis
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


        // X Axis
        const xAxis = d3.axisBottom(xScale)
            .tickSizeInner(-height + margin.bottom)
            .tickSizeOuter(0)
            .tickPadding(10)
            .ticks(12);

        newChart.append('g')
            .attr('class', 'chart-axisChartAxis-Shape')
            .attr('transform', 'translate(0,' + height + ')')
            .call(xAxis);


        const xAxisTop = d3.axisBottom(xScale)
            .ticks(0);

        newChart.append('g')
            .attr('class', 'chart-axis')
            .attr('transform', 'translate(0, ' + margin.bottom + ')')
            .call(xAxisTop);

        const yAxisRight = d3.axisLeft(yScale)
            .ticks(0);

        newChart.append('g')
            .attr('class', 'chart-axis')
            .attr('transform', 'translate(' + width + ', 0)')
            .call(yAxisRight);


        const meanTimes = [];
        let lastPoint = (data.readings[0][0]);

        for (j = 0; j < data.readings.length; j++) {
            meanTimes.push((data.readings[j][0] - lastPoint) * 0.0001);
            lastPoint = data.readings[j][0];
        }
        meanTimes.sort();
        const meanTime = meanTimes[parseInt(meanTimes.length / 2)];
        let last = 0;

        const lineFunction = d3.line()
            .defined((d) => {
                d[0] = parseInt(d[0]);
                if (d[0] < start / 1000 || d[0] > end / 1000) {
                    return false;
                }
                if (d[1] > max || d[1] < min) {
                    scope.newGraph.warning = 'Warning: Some data points are not shown in graph and may be causing line breaks.';
                    return false;
                }

                const val = (d[0] - last) * 0.0001;
                if (val > meanTime * 1.5 || val < meanTime * 0.5) {
                    last = d[0];
                    return false;
                }
                last = d[0];
                return true;
            })
            .x((d) => {
                return isNaN(xScale(d[0] * 1000)) ? 0 : xScale(d[0] * 1000);
            })
            .y((d) => {
                return yScale(d[1]);
            });
        newChart.append('path')
            .attr('d', lineFunction(data.readings))
            .attr('stroke', '#FFB90F')
            .attr('stroke-width', 2)
            .attr('fill', 'none');

        // TOOL-TIPS
        // ooltip container
        const tooltip = newChart.append('g')
            .style('display', 'none');

        const circleElements = [];
        const textElements = [];

        // for every stream. create a circle, text,
        // and horizontal line element and store in an array
        const newCircle = tooltip.append('circle')
            .attr('class', 'tooltip-circle')
            .style('fill', 'none')
            .style('stroke', 'blue')
            .attr('r', 4);
        circleElements.push(newCircle);

        const newText = tooltip.append('text')
            .attr('width', 100 * 2)
            .attr('height', 100 * 0.4)
            .attr('fill', 'black');

        textElements.push(newText);

        // Y-axis line for tooltip
        const yLine = tooltip.append('g')
            .append('line')
            .attr('class', 'tooltip-line')
            .style('stroke', 'blue')
            .style('stroke-dasharray', '3,3')
            .style('opacity', 0.5)
            .attr('y1', margin.bottom)
            .attr('y2', height);

        // Date text
        const timeText = tooltip.append('text')
            .attr('x', 0)
            .attr('y', margin.bottom - 5)
            .attr('width', 100)
            .attr('height', 100 * 0.4)
            .attr('fill', 'black');

        const myData = [];
        data.readings.forEach((reading) => {
            myData.push(new Date(reading[0]).getTime() * 1000);
        });

        // Selection box
        const selectionBox = newChart.append('rect')
            .attr('fill', 'none')
            .attr('opacity', 0.5)
            .attr('x', 0)
            .attr('y', margin.bottom)
            .attr('width', 14)
            .attr('height', height - margin.bottom)
            .attr('class', 'myselection');

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
                d = x0 - d0[0] * 1000 > d1[0] * 1000 - x0 ? d1 : d0;
                if (xScale(d[0] * 1000) > dragStartPos) {
                    selectionBox.attr('width', (xScale(d[0] * 1000) - dragStartPos));
                } else {
                    selectionBox.attr('width', (dragStartPos - xScale(d[0] * 1000)));
                    selectionBox.attr('transform', 'translate(' + xScale(d[0] * 1000) + ',0)');
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
        // Hit area for selection box
        newChart.append('rect')
            .attr('width', width)
            .attr('height', height)
            .style('fill', 'none')
            .style('pointer-events', 'all')
            .on('mouseover', () => {
                tooltip.style('display', null);
            })
            .on('mouseout', () => {
                tooltip.style('display', 'none');
            })
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
                    if (x0 - d0[0] * 1000 > d1[0] * 1000 - x0) {
                        d = d1;
                    } else {
                        d = d0;
                    }
                }
                if (d[1] < min || d[1] > max) {
                    return;
                }
                circleElements[0].attr('transform', 'translate(' + xScale(d[0] * 1000) + ',' + yScale(d[1]) + ')');
                yLine.attr('transform', 'translate(' + xScale(d[0] * 1000) + ',' + 0 + ')');
                timeText.text(new Date(d[0] * 1000) + ' | ' + this.FormatText(d[1]));

                textElements[0]
                    .text(this.FormatText(d[1]))
                    .attr('transform', 'translate(' + (xScale(d[0] * 1000) + 10) + ',' + (yScale(d[1]) - 10) + ')');

            })
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
                const d = x0 - d0[0] * 1000 > d1[0] * 1000 - x0 ? d1 : d0;
                selectionBox.attr('transform', 'translate(' + xScale(d[0] * 1000) + ',0)');
                dragStartPos = xScale(d[0] * 1000);
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
