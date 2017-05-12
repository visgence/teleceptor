/*jslint node: true */
'use strict';
var angular, $;

angular.module('teleceptor.maincontroller', [])

.controller('mainController', ['$scope', '$location', function($scope, $location){
    $scope.mainPage = true;
    if($location.search().json !== undefined){
        $scope.mainPage = false;
    }


    $scope.page = function(i){
        $scope.mainPage = i;
        if(i){
            $location.search('json', null);
        } else {
            $location.search('json', 1);
        }
    };

    $scope.addInput = function() {
        console.log("Add input clicked");
        $("#input-section").append(createSensorInput());

    };

    $scope.addOutput = function() {
        console.log("Add output clicked");
        $("#output-section").append(createSensorOutput());

    };

    $scope.submit = function() {
        var jsonData = {};

        jsonData.uuid = angular.element('#uuid').val();
        jsonData.model = angular.element('#model').val();
        jsonData.description = angular.element('#description').val();

        var inputs = [];
        var outputs = [];
        $(".sensor-input").each(function(index) {
            var input = {};
            input.name = angular.element('input[name="name"]').val();
            input.description = angular.element('input[name="description"]').val();
            input.sensor_type = angular.element('input[name="sensor_type"]').val();
            input.units = angular.element('input[name="units"]').val();
            inputs.push(input);

        });

        $(".sensor-output").each(function(index) {
            var output = {};
            output.name =angular.element('input[name="name"]').val();
            output.model = angular.element('input[name="model"]').val();
            output.description = angular.element('input[name="description"]').val();
            output.sensor_type = angular.element('input[name="sensor_type"]').val();
            output.units = angular.element('input[name="units"]').val();
            output.timestamp = Number(angular.element('input[name="timestamp"]').val());

            var scale = [];
            scale.push(Number(angular.element('input[name="scale1"]').val()));
            scale.push(Number(angular.element('input[name="scale2"]').val()));
            output.scale = scale;

            outputs.push(output);

        });

        jsonData.out = outputs;
        jsonData.in = inputs;

        var json = JSON.stringify(jsonData);
        var jsonLength = json.length;

        if ($('#escape').is(":checked")) {

            json = escape(json);

        }

        console.log(json);

        $('#jsonLength').html(jsonLength);
        $('#jsonData').html(json);
        $('#jsonModal').modal('show');

        return false;
    };


function escape(text) {
    return text.replace(/"/g, '\\"');
}

function createInput(label, name) {

    var input = $("<input/>", {
        //id: "id",
        name : name,
        type : "text",
        placeholder : name,
        "class" : "form-control input-md"
    });

    label = $("<label/>", {
        "class" : "col-md-5 control-label",
        //"for": id
    }).html(label);

    var group = $("<div/>", {
        "class" : "form-group"
    });

    var col = $("<div/>", {
        "class" : "col-md-4"
    });

    group.append(label);
    col.append(input);
    group.append(col);

    return group;

}

function createButton(desc, name, toRemove) {

    var button = $("<button/>", {
        //id: uuid,
        name : name,
        "class" : "btn btn-danger"
    }).html(desc);

    var label = $("<label/>", {
        "class" : "col-md-5 control-label",
        //"for": id
    }).html(desc);

    var group = $("<div/>", {
        "class" : "form-group"
    });

    var col = $("<div/>", {
        "class" : "col-md-4"
    });

    button.click(function() {
        console.log("button click");
        toRemove.remove();
        return false;
    });

    group.append(label);
    col.append(button);
    group.append(col);

    return group;
}

function createSensorInput() {

    var sensor = $("<div/>", {
        "class" : "sensor-input",
        "style" : "padding-bottom: 30px"
    });

    sensor.append(createInput("Name", "name"));
    sensor.append(createInput("Type", "sensor_type"));
    sensor.append(createInput("Units", "units"));
    sensor.append(createInput("Description", "description"));
    sensor.append(createButton("Remove", "remove", sensor));

    return sensor;
}

function createSensorOutput() {

    var sensor = $("<div/>", {
        "class" : "sensor-output",
        "style" : "padding-bottom: 30px"
    });

    sensor.append(createInput("Name", "name"));
    sensor.append(createInput("Type", "sensor_type"));
    sensor.append(createInput("Units", "units"));
    sensor.append(createInput("model", "model"));
    sensor.append(createInput("Description", "description"));
    sensor.append(createInput("Timestamp", "timestamp"));
    sensor.append(createInput("Scale Cof 1", "scale1"));
    sensor.append(createInput("Scale Cof 2", "scale2"));
    sensor.append(createButton("Remove", "remove", sensor));

    return sensor;
}
}]);