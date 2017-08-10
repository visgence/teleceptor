export default class generateJsonController {
    constructor($scope, $mdDialog) {
        'ngInject';

        this.$scope = $scope;
        this.$mdDialog = $mdDialog;

    }
    $onInit() {
        this.$scope.inputItems = [];
        this.$scope.outputItems = [];
        this.$scope.escape = false;

        //  intialize input object
        this.$scope.addInput = () => {
            this.$scope.inputItems.push({
                name: '',
                type: '',
                units: '',
                description: '',
            });

        };

        //  pop top object on remove button press
        this.$scope.removeInput = () => {

            this.$scope.inputItems.pop();

        };

        this.$scope.removeOutput = () => {

            this.$scope.outputItems.pop();

        };

        //  intialize output objects
        this.$scope.addOutput = () => {
            this.$scope.outputItems.push({
                name: '',
                model: '',
                type: '',
                units: '',
                description: '',
                scale_cof: '',
            });
        };

        //  on submit button press
        this.$scope.submit = () => {
            const jsonData = {};

            jsonData.uuid = this.$scope.uuid;
            jsonData.model = this.$scope.model;
            jsonData.description = this.$scope.description;

            const inputs = [];
            const outputs = [];

            //  loops to pull correct items out of input/output object arrays.
            for (let i = 0; i < this.$scope.inputItems.length; i++) {
                const input = {};
                input.name = this.$scope.inputItems[i].name;
                input.description = this.$scope.inputItems[i].description;
                input.sensor_type = this.$scope.inputItems[i].sensor_type;
                input.units = this.$scope.inputItems[i].units;
                inputs.push(input);
            }

            for (let i = 0; i < this.$scope.outputItems.length; i++) {
                const output = {};

                output.name = this.$scope.outputItems[i].name;
                output.model = this.$scope.outputItems[i].model;
                output.description = this.$scope.outputItems[i].description;
                output.sensor_type = this.$scope.outputItems[i].type;
                output.units = this.$scope.outputItems[i].units;

                let coefficients = this.$scope.outputItems[i].scale_cof;
                coefficients = coefficients.split(',');
                const cleanCoefficients = [];

                coefficients.forEach((coefficients) => {
                    // only allow 0-9, -, .
                    cleanCoefficients.push(coefficients.replace(/[^0-9\-\.]/g, ''));
                });

                output.scale = {
                    coefficients: cleanCoefficients,
                    timestamp: new Date().getTime(),
                };

                outputs.push(output);
            }

            $('.sensor-output').each((index) => {
                const scale = [];
                scale.push(Number($('input[name="scale1"]').val()));
                scale.push(Number($('input[name="scale2"]').val()));
                output.scale = scale;
                outputs.push(output);
            });

            jsonData.out = outputs;
            jsonData.in = inputs;

            let json = JSON.stringify(jsonData);
            const jsonLength = json.length;

            //  check if escape has been checked
            if (this.$scope.escape) {
                json = this.escape(json);
            }

            // use material alert dialog to present finished JSON
            this.$mdDialog.show(
                this.$mdDialog.alert()
                    .parent(angular.element(document.querySelector('#popupContainer')))
                    .clickOutsideToClose(true)
                    .title('JSON Data, Length ' + jsonLength + ' bytes')
                    .textContent(json)
                    .ariaLabel('Alert Dialog Demo')
                    .ok('Close'),
            );
            return false;
        };

    }
    escape(text) {
        return text.replace(/"/g, '\\"');
    }

}
