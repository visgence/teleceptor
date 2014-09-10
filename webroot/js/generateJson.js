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

function escape(text) {return text.replace(/"/g,'\\"')};

function createInput(label,name) {
    
  input = $("<input/>", 
    {
        //id: "id",
        name: name,
        type: "text",
        placeholder: name,
        "class": "form-control input-md"  
    });

  label = $("<label/>", 
    {
        "class": "col-md-5 control-label",
        //"for": id   
    }).html(label);    

  group = $("<div/>", 
    {
        "class":"form-group"    
    });


   col = $("<div/>",
    {
        "class":"col-md-4"   
    });

   group.append(label);
   col.append(input);
   group.append(col);
    
   return group;

};

function createSensorInput() {
    
    sensor = $("<div/>",
    {
        "class":"sensor-input",
        "style":"padding-bottom: 30px"   
    });
    
    sensor.append(createInput("Name","name"));
    sensor.append(createInput("Type","sensor_type"));
    sensor.append(createInput("Units","units"));
    sensor.append(createInput("Description","description"));
    
    
    return sensor;
}

function createSensorOutput() {
    
    sensor = $("<div/>",
    {
        "class":"sensor-output",
        "style":"padding-bottom: 30px"   
    });
    
    sensor.append(createInput("Name","name"));
    sensor.append(createInput("Type","sensor_type"));
    sensor.append(createInput("Units","units"));
    sensor.append(createInput("model","model"));
    sensor.append(createInput("Description","description"));
    sensor.append(createInput("Timestamp","timestamp"));
    sensor.append(createInput("Scale Cof 1","scale1"));
    sensor.append(createInput("Scale Cof 2","scale2"));
    
    
    return sensor;
}


$(function($) {


    $("#add-input").click(function() {
       console.log("Add input clicked"); 
       $("#input-section").append(createSensorInput());
        
        
    });


    $("#add-output").click(function() {
       console.log("Add output clicked");
       $("#output-section").append(createSensorOutput());
        
        
        
    });

    $('form').submit(function() {
        var jsonData = {};

        jsonData.uuid = $(this).find('#uuid').val();
        jsonData.model = $(this).find('#model').val();
        jsonData.description = $(this).find('#description').val();

        inputs =[];
        outputs =[];
        $(".sensor-input").each(function(index){
            input ={};
            input.name = $(this).find('input[name="name"]').val();    
            input.description = $(this).find('input[name="description"]').val();    
            input.sensor_type = $(this).find('input[name="sensor_type"]').val();    
            input.units = $(this).find('input[name="units"]').val();    
            inputs.push(input);
            
        });
        
        $(".sensor-output").each(function(index){
            output ={};
            output.name = $(this).find('input[name="name"]').val();    
            output.model = $(this).find('input[name="model"]').val();    
            output.description = $(this).find('input[name="description"]').val();    
            output.sensor_type = $(this).find('input[name="sensor_type"]').val();    
            output.units = $(this).find('input[name="units"]').val();    
            output.timestamp = Number($(this).find('input[name="timestamp"]').val());    
            
            scale = [];
            scale.push(Number($(this).find('input[name="scale1"]').val()));    
            scale.push(Number($(this).find('input[name="scale2"]').val()));    
            output.scale = scale;

            outputs.push(output);
            
        });
        
        jsonData["out"] = outputs;
        jsonData["in"] = inputs;

        json = JSON.stringify(jsonData);
   
        if ($('#escape').is(":checked")) {
            
            json = escape(json);
            
        }

        console.log(json);
        $('#jsonData').html(json);
        $('#jsonModal').modal('show'); 

        return false;
    });

}); 