export default class sensorController { // ', ['frapontillo.bootstrap-switch',])

    constructor(infoService, apiService, $scope, $location) {
        'ngInject';

        this.$scope = $scope;
        this.$location = $location;
        this.apiService = apiService;
        this.infoService = infoService;

        this.$scope.$watch(() => this.infoService.getStream(), (nv, ov) => {
            if (nv === undefined) {
                return;
            }
            if (nv.sensor === undefined) {
                return;
            }
            this.LoadSensor(nv.sensor);
        });
    }

    $onInit() {
        // tabs:
        // config, entry, export, command, metatdata
        this.$scope.tab = 'config';
        this.$scope.isSelected = 'yep'; // For the bootstrap switch in command.
        this.$scope.isActive = 'false';
        this.$scope.ShowInfo = false;

        this.$scope.ChangeTab = (event, tab) => {
            this.$scope.tab = tab;
            $('.nav-tabs li').removeClass('active');
            $(event.target.parentNode).toggleClass('active');
        };

        this.$scope.EditFields = () => {
            this.$scope.editing = true;
            this.$scope.previous_coefficients = this.$scope.sensor.last_calibration.coefficients;
        };

        this.$scope.CancelFields = () => {
            this.$scope.editing = false;
        };

        this.$scope.SendData = () => {
            const sensorInfo = infoService.getSensor();
            const id = sensorInfo.uuid;
            const newValue = angular.element('#manual-entry')[0].value;
            const time = (new Date()).getTime() / 1000;

            const sensorReading = {
                name: id,
                sensor_type: sensorInfo.sensor_type,
                timestamp: time,
                meta_data: {},
            };

            const payload = [{
                info: {
                    uuid: '',
                    name: sensorInfo.name,
                    description: sensorInfo.description,
                    out: (sensorInfo.isInput ? [] : [sensorReading]),
                    in: (sensorInfo.isInput ? [sensorReading] : []),
                },
                readings: [
                    [id, newValue, time],
                ],
            }];
            this.apiService.post('station', payload)
                .then((success) => {
                    console.log(success);
                })
                .catch((error) => {
                    console.log('error');
                    console.log(error);
                });
        };

        this.$scope.SaveFields = () => {
            const updateData = {};
            const url = 'sensors';
            const editableFields = ['last_calibration', 'units', 'description', 'uuid'];

            Object.keys(this.$scope.sensor).forEach((key) => {
                if (!(editableFields.includes(key))) {
                    return;
                }
                if (this.$scope.sensor[key] === '-' || this.$scope.sensor[key] === '') {
                    updateData[key] = null;
                } else {
                    updateData[key] = this.$scope.sensor[key];
                }
            });
            if (updateData.last_calibration.coefficients !== this.$scope.previous_coefficients) {
                updateData.last_calibration.timestamp = Date.now() / 1000;
            }

            this.apiService.put(url, updateData)
                .then((success) => {
                    this.$scope.editing = false;
                    // TODO: This needs to be better, a simple refresh of sensor info and maybe the graph units.
                    location.reload();
                })
                .catch((error) => {
                    console.log('Error Occured: ', error.data);
                });
        };

        this.$scope.CommandSwitch = () => {
            sendCommand();
        };

        this.$scope.ExportES = () => {
            let start = this.$location.search().start;
            if (start === undefined) {
                start = new Date().getTime() - 24 * 60 * 60 * 1000;
            }
            let end = this.$location.search().end;
            if (end === undefined) {
                end = new Date().getTime();
            }
            console.log(start, end);

            const readingsUrl = 'readings?datastream=' +
                this.infoService.getStream().id +
                '&start=' + parseInt(start / 1000) +
                '&end=' + parseInt(end / 1000) +
                '&source=ElasticSearch';
            this.apiService.get(readingsUrl)
                .then((success) => {
                    this.exportData(success.data.readings);
                })
                .catch((error) => {
                    console.log('error');
                    console.log(error);
                });
        };

        this.$scope.ExportSQL = () => {
            let start = this.$location.search().start;
            if (start === undefined) {
                start = new Date().getTime() - 24 * 60 * 60 * 1000;
            }
            let end = this.$location.search().end;
            if (end === undefined) {
                end = new Date().getTime();
            }
            const readingsUrl = 'readings?datastream=' +
                this.infoService.getStream().id +
                '&start=' + parseInt(start / 1000) +
                '&end=' + parseInt(end / 1000) +
                '&source=SQL';
            this.apiService.get(readingsUrl)
                .then((success) => {
                    this.exportData(success.data.readings);
                })
                .catch((error) => {
                    console.log('error');
                    console.log(error);
                });
        };

        this.$scope.EntrySend = () => {
            const sensorInfo = this.$scope.sensor;
            const id = sensorInfo.uuid;
            const newValue = this.$scope.EntryValue;
            const time = (new Date()).getTime() / 1000;

            const sensorReading = {
                name: id,
                sensor_type: sensorInfo.sensor_type,
                timestamp: time,
                meta_data: {},
            };

            const payload = [{
                info: {
                    uuid: '',
                    name: sensorInfo.name,
                    description: sensorInfo.description,
                    out: (sensorInfo.isInput ? [] : [sensorReading]),
                    in: (sensorInfo.isInput ? [sensorReading] : []),
                },
                readings: [
                    [id, newValue, time],
                ],
            }];

            this.apiService.post('station', payload)
                .then((success) => {
                    console.log(success);
                })
                .catch((error) => {
                    console.log('error');
                    console.log(error);
                });
        };

        // CONVERT TO SCOPE
        $('#sendCommand').on('click', () => {
            this.sendCommand();
        });
    }

    // This needs to wait for stream info to be set, then make request by sensor uuid
    LoadSensor(sensor) {
        this.apiService.get('sensors/' + sensor)
            .then((success) => {
                this.$scope.sensor = success.data.sensor;
                this.$scope.ShowInfo = true;

                if (success.data.sensor_type === 'output') {
                    this.$scope.isActive = true;
                    // We need to set the preliminary state
                } else {
                    this.$scope.isActive = false;
                }
                $('#sensor-card').css('visibility', 'visible');
            })
            .catch((error) => {
                console.log('error');
                console.log(error);
            });
    }

    exportData(readings) {
        const sensorInfo = this.$scope.sensor;
        if (readings === null) {
            readings = this.infoService.getReadings();
        }

        const scaledReadings = [];
        const coefficients = sensorInfo.last_calibration.coefficients.replace('[', '').replace(']', '').replace(' ', '').split(',');
        let i;
        for (i = 0; i < readings.length; i++) {
            scaledReadings.push(readings[i][1] * parseInt(coefficients[0]) + parseInt(coefficients[1]));
        }

        // actual delimiter characters for CSV format
        const colDelim = ',';
        const rowDelim = '\r\n';

        // build csv string
        let csv = '';
        csv += 'timestamp' + colDelim + 'UUID' + colDelim + 'value' + colDelim + 'scaled value' + colDelim + 'units' + rowDelim;
        for (i = 0; i < readings.length; i++) {
            csv += readings[i][0] +
                colDelim + sensorInfo.uuid +
                colDelim + readings[i][1] +
                colDelim + scaledReadings[i] +
                colDelim + sensorInfo.units +
                rowDelim;
        }
        // Data URI
        const today = new Date();

        const downloadFilename = sensorInfo.uuid + '_' +
            today.getMonth() +
            1 + '-' +
            today.getDate() + '-' +
            today.getFullYear() + '_' +
            today.getHours() + ':' +
            today.getMinutes() + '.csv';

        // actually download
        const link = document.createElement('a');
        link.download = downloadFilename;
        link.href = 'data:application/csv;charset=utf-8,' + encodeURIComponent(csv);
        link.click();
    }

    // UNTESTED
    sendCommand() {
        const sensorInfo = infoService.getSensor();
        // p ost new value to commands api
        const payload = {
            message: angular.element('#bs-switch')[0].value,
            duration: 60000,
            sensor_id: sensorInfo.uuid,
        };
        apiService.post('messages/', payload)
            .then((success) => {
                console.log('the response was:');
                console.log(success);
            })
            .catch((error) => {
                console.log('error');
                console.log(error);
            });
    }
}
