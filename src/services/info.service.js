export default class infoService {

    // Set by stream info.
    setStream(stream) {
        this.stream = stream;
    }

    // Used by stream info
    getStream() {
        if (this === undefined) {
            return '';
        }
        return this.stream;
    }

    // Set by sensor info.
    setSensor(sensor) {
        sensor.last_calibration.coefficients = JSON.stringify(sensor.last_calibration.coefficients);
        this.sensor = sensor;
    }

    // Used by graph and sensor info.
    getSensor() {
        return this.sensor;
    }

    // Set by graph
    setReadings(readings) {
        this.readings = readings;
    }

    // Used by sensor (export)
    getReadings() {
        return this.readings;
    }
}
