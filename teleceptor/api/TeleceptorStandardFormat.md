This is the standard format used when using the api.

[{
    "info":{
        "uuid": "sensor_uuid",
        "name": "My first sensor.",
        "description": "demonstrates the Teleceptor standard format."
        "rev" : "1.0",
        "in"  : [{
            "name"  : "in1",
            "scale" : [1,2,3...],
            ...
        },{
            "name"  : "in2",
            "scale" : [1,2,3,...],
            ...
        }]
        "out" : [{
            "name"  : "out1",
            "scale" : [1,2,3,...],
            ...
        },{
            "name"  : "out2",
            "scale" : [1,2,3,...],
            ...
        }]
    }
    "readings":[
        [in1, val, time],
        [out2, val, time],
        ...
    ]
}]
