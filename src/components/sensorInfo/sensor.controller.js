import {
    showSuccess,
    showError,
} from '../../utilites/dialogs.utils';

export default class sensorController {

    constructor(infoService, apiService, $scope, $location, $mdToast, $mdDialog) {
        'ngInject';

        this.$scope = $scope;
        this.$location = $location;
        this.apiService = apiService;
        this.infoService = infoService;
        this.$mdToast = $mdToast;
        this.$mdDialog = $mdDialog;

        this.$scope.$watch(() => this.infoService.getStream(), (nv, ov) => {
            if (nv === undefined || nv === ov) {
                return;
            }
            if (nv.sensor === undefined) {
                return;
            }
            this.loadSensor(nv.sensor);
            this.loadCalibrations(nv.sensor);
        });

        $scope.displayInfo = $location.search().datastream !== undefined;
    }

    $onInit() {
        // tabs:
        // config, entry, export, command, metatdata, calibrations
        this.$scope.tab = 'config';
        this.$scope.isActive = 'false';
        this.$scope.ShowInfo = false;
        this.$scope.sensorLoaded = false;

        this.$scope.ChangeTab = (event, tab) => {
            this.$scope.tab = tab;
            $('.nav-tabs li').removeClass('active');
            $(event.target.parentNode).toggleClass('active');
        };

        this.$scope.EditFields = () => {
            this.$scope.editing = true;
            this.$scope.previous_coefficients = this.$scope.sensor.last_calibration.coefficients; // eslint-disable-line
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
                sensor_type: sensorInfo.sensor_type, // eslint-disable-line
                timestamp: time,
                meta_data: {}, // eslint-disable-line
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
                    showSuccess(this.$mdToast);
                })
                .catch((error) => {
                    showError(this.$mdDialog, error);
                    console.error(error);
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
            try {
                this.apiService.put(url, updateData)
                    .then((success) => {
                        showSuccess(this.$mdToast);
                        this.infoService.setSensor(success.data.sensor);
                        this.$scope.sensor = this.infoService.getSensor();
                        this.$scope.editing = false;
                        this.loadCalibrations(this.$scope.sensor.uuid);
                    })
                    .catch((error) => {
                        console.error(error);
                        showError(this.$mdDialog, error);
                    });
            } catch (error) {
                console.error('error');
                showError(this.$mdDialog, error);
            }
        };

        this.$scope.CommandSwitch = () => {
            sendCommand();
        };

        this.$scope.ExportData = (source) => {
            let start = this.$location.search().start;
            if (start === undefined) {
                start = parseInt(new Date().getTime() - 24 * 60 * 60 * 1000);
            }
            let end = this.$location.search().end;
            if (end === undefined) {
                parseInt(end = new Date().getTime());
            }
            const streamId = this.infoService.getStream().id;
            const readingsUrl = `readings?datastream=${streamId}&start=${start}&end=${end}&source=${source}`;
            this.apiService.get(readingsUrl)
                .then((success) => {
                    if (success.data.error !== undefined) {
                        showError(this.$mdDialog, 'No readings could be found in current time range.');
                    } else {
                        this.exportData(success.data.readings);
                    }
                })
                .catch((error) => {
                    console.error('error');
                    showError(this.$mdDialog, error);
                });
        };

        this.$scope.EntrySend = () => {
            const sensorInfo = this.$scope.sensor;
            const id = sensorInfo.uuid;
            const newValue = this.$scope.EntryValue;
            const time = (new Date()).getTime() / 1000;

            const sensorReading = {
                name: id,
                sensor_type: sensorInfo.sensor_type, // eslint-disable-line
                timestamp: time,
                meta_data: {}, // eslint-disable-line
            };

            if (isNaN(newValue)) {
                console.error('error');
                showError(this.$mdDialog, 'New data must be a number');
                return;
            }

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
                    showSuccess(this.$mdToast, 'Point has been entered.');
                })
                .catch((error) => {
                    console.error('error');
                    showError(this.$mdDialog, error);
                });
        };

        // Untested
        this.$scope.sendCommand = () => {
            const sensorInfo = infoService.getSensor();
            // post new value to commands api
            const payload = {
                message: this.$scope.commandSwitch.value,
                duration: 60000,
                sensor_id: sensorInfo.uuid, // eslint-disable-line
            };
            apiService.post('messages/', payload)
                .then((success) => {
                    showSuccess(this.$mdToast);
                })
                .catch((error) => {
                    console.error('error');
                    showError(this.$mdDialog, error);
                });
        };
    }

    // This needs to wait for stream info to be set, then make request by sensor uuid
    loadSensor(sensor) {
        this.apiService.get(`sensors/${sensor}`)
            .then((success) => {
                this.$scope.sensor = success.data.sensor;
                this.infoService.setSensor(success.data.sensor);
                this.$scope.ShowInfo = true;
                this.$scope.Date = new Date(this.$scope.sensor.last_calibration.timestamp * 1000);
                this.$scope.Date = `${this.$scope.Date.toDateString()}, ${this.$scope.Date.getHours()}:${this.$scope.Date.getMinutes()}`;

                if (success.data.sensor_type === 'output') {
                    this.$scope.isActive = true;
                    // We need to set the preliminary state
                    this.$scope.commandSwitch = true || false;
                } else {
                    this.$scope.isActive = false;
                    this.$scope.commandSwitch = false;
                }
                $('#sensor-card').css('visibility', 'visible');
            })
            .catch((error) => {
                console.error('error');
                showError(this.$mdDialog, error);
            });
    }

    // This needs to wait for stream info to be set, then make request by sensor uuid
    loadCalibrations(sensor) {
        this.apiService.get(`calibrations?sensor_id=${sensor}`)
            .then((success) => {
                this.$scope.calibrations = {};
                success.data.calibrations.forEach((calibration) => {
                    this.$scope.calibrations[new Date(calibration.timestamp * 1000)] = calibration.coefficients;
                });
            })
            .catch((error) => {
                console.error(error);
                showError(this.$mdDialog, error);
            });
    }

    exportData(data) {
        let readings = data;
        const sensorInfo = this.$scope.sensor;
        if (readings === null || readings.length === 0) {
            readings = this.infoService.getReadings();
        }

        const scaledReadings = [];
        const coefficients = sensorInfo.last_calibration.coefficients
            .replace(/\[/g, '')
            .replace(/\]/g, '')
            .split(',');

        let index;
        let units;

        for (index = 0; index < readings.length; index++) {
            scaledReadings.push(readings[index][1] * (parseFloat(coefficients[0])) + parseFloat(coefficients[1]));
        }

        // actual delimiter characters for CSV format
        const colDelim = ',';
        const rowDelim = '\r\n';

        // build csv string
        if (sensorInfo.units === null) {
            units = 'none';
        } else {
            units = sensorInfo.units;
        }

        let csv = `timestamp${colDelim}UUID${colDelim}value${colDelim}scaled value${colDelim}units${rowDelim}`;

        for (index = 0; index < readings.length; index++) {
            csv += readings[index][0] +
                colDelim + sensorInfo.uuid +
                colDelim + readings[index][1] +
                colDelim + scaledReadings[index] +
                colDelim + units +
                rowDelim;
        }
        // Data URI
        const today = new Date();

        const downloadFilename = `${sensorInfo.uuid}_${today.getMonth()}-${today.getDate()}-${today.getFullYear()}_${today.getHours()}:${today.getMinutes()}.csv`;

        // actually download
        const link = document.createElement('a');
        link.download = downloadFilename;
        link.href = `data:application/csv;charset=utf-8,${encodeURIComponent(csv)}`;
        link.click();
    }
}
