export default class generateJsonController {
    constructor($scope) {
        'ngInject';

        this.$scope = $scope;

    }
    $onInit() {
        this.$scope.addInput = () => {
            $('#input-section').append(this.createSensorInput());
        };

        this.$scope.addOutput = () => {
            $('#output-section').append(this.createSensorOutput());
        };

        this.$scope.submit = () => {
            const jsonData = {};

            jsonData.uuid = $('#uuid').val();
            jsonData.model = $('#model').val();
            jsonData.description = $('#description').val();

            const inputs = [];
            const outputs = [];
            $('.sensor-input').each((index) => {
                const input = {};
                input.name = $('input[name="name"]').val();
                input.description = $('input[name="description"]').val();
                input.sensor_type = $('input[name="sensor_type"]').val();
                input.units = $('input[name="units"]').val();
                inputs.push(input);
            });

            $('.sensor-output').each((index) => {
                const output = {};
                output.name = $('input[name="name"]').val();
                output.model = $('input[name="model"]').val();
                output.description = $('input[name="description"]').val();
                output.sensor_type = $('input[name="sensor_type"]').val();
                output.units = $('input[name="units"]').val();
                output.timestamp = Number($('input[name="timestamp"]').val());

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

            if ($('#escape').is(':checked')) {
                json = this.escape(json);
            }
            $('#json-length').html(jsonLength);
            $('#json-data').html(json);
            $('#json-modal').modal('show');
            return false;
        };
    }
    escape(text) {
        return text.replace(/"/g, '\\"');
    }

    createInput(label, name) {
        const input = $('<input/>', {
            name: name,
            type: 'text',
            placeholder: name,
            class: 'form-control input-md',
        });

        label = $('<label/>', {
            class: 'col-md-5 control-label',
            // 'for': id
        }).html(label);

        const group = $('<div/>', {
            class: 'form-group',
        });

        const col = $('<div/>', {
            class: 'col-md-4',
        });

        group.append(label);
        col.append(input);
        group.append(col);

        return group;
    }

    createButton(desc, name, toRemove) {
        const button = $('<button/>', {
            // id: uuid,
            name: name,
            class: 'btn btn-danger',
        }).html(desc);

        const label = $('<label/>', {
            class: 'col-md-5 control-label',
            // 'for': id
        }).html(desc);

        const group = $('<div/>', {
            class: 'form-group',
        });

        const col = $('<div/>', {
            class: 'col-md-4',
        });
        button.click(() => {
            console.log('button click');
            toRemove.remove();
            return false;
        });
        group.append(label);
        col.append(button);
        group.append(col);
        return group;
    }

    createSensorInput() {
        const sensor = $('<div/>', {
            class: 'sensor-input',
            style: 'padding-bottom: 30px',
        });
        sensor.append(this.createInput('Name', 'name'));
        sensor.append(this.createInput('Type', 'sensor_type'));
        sensor.append(this.createInput('Units', 'units'));
        sensor.append(this.createInput('Description', 'description'));
        sensor.append(this.createButton('Remove', 'remove', sensor));
        return sensor;
    }

    createSensorOutput() {
        const sensor = $('<div/>', {
            class: 'sensor-output',
            style: 'padding-bottom: 30px',
        });
        sensor.append(this.createInput('Name', 'name'));
        sensor.append(this.createInput('Type', 'sensor_type'));
        sensor.append(this.createInput('Units', 'units'));
        sensor.append(this.createInput('model', 'model'));
        sensor.append(this.createInput('Description', 'description'));
        sensor.append(this.createInput('Timestamp', 'timestamp'));
        sensor.append(this.createInput('Scale Cof 1', 'scale1'));
        sensor.append(this.createInput('Scale Cof 2', 'scale2'));
        sensor.append(this.createButton('Remove', 'remove', sensor));
        return sensor;
    }
}
