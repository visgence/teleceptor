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


    /** Validates an observable that it has some value in it else set's an error message and boolean flag on the observable.

        @param overrideMessage {string} Error message to store on the observable should validation fail.
        @return {observable} New observable
    */
    ko.extenders.required = function(target, overrideMessage) {
        target.hasError = ko.observable();
        target.validationMessage = ko.observable();

        target.validate = function() {
            var value = target();
            if(typeof(value) === "string")
                value = value.trim();

            target.hasError(value ? false : true);
            target.validationMessage(value ? "" : overrideMessage || "")

            //Return inverse to say whether or not validation succeeded or failed for target
            return !target.hasError();
        };

        return target;
    };


    /**
        Returns back a compputed that forces the observable to only contain numberic values.

        Precision of the numeric values typed and the starting default value should be given.

        @param {plain object} args Contains 'precision' and 'default' as numeric values
        @return {computed} New computed observable
    */
    ko.extenders.numeric = function(target, args) {
        var precision = args['precision'];
        var defaultStart = args['default'];

        //create a writeable computed observable to intercept writes to our observable
        var result = ko.computed({
            read: target,  //always return the original observables value
            write: function(newValue) {
                var current = target(),
                    roundingMultiplier = Math.pow(10, precision),
                    newValueAsNum = isNaN(newValue) ? (isNaN(current) ? defaultStart : current) : parseFloat(+newValue),
                    valueToWrite = Math.round(newValueAsNum * roundingMultiplier) / roundingMultiplier;

                //only write if it changed
                if (valueToWrite !== current) {
                    target(valueToWrite);
                } else {
                    //if the rounded value is the same, but a different value was written, force a notification for the current field
                    if (newValue !== current) {
                        target.notifySubscribers(valueToWrite);
                    }
                }
            }
        }).extend({ notify: 'always' });

        //initialize with current value to make sure it is rounded appropriately
        result(target());

        //return the new computed observable
        return result;
    }


    /**
        Adds an observable on the target for storing epoch seconds converted from the original value.  Mainly usefull when
        paired with datetimepicker that need to be bound to observables and you want to store/get the date as epoch for a
        server call.

        target get attr called epochValue as the new observable and is set each time the original target is set with a value.
        In case of empty string epochValue will contain undefined, the default value of observables.
    */
    ko.extenders.epoch = function(target) {

        target.epochValue = ko.observable();
        target.subscribe(function(newVal) {
            if (typeof(newVal) == 'number')
                target.epochValue(newVal);
            else if (newVal !== '')
                target.epochValue((new Date(newVal)).getTime() / 1000);
            else
                target.epochValue(null);

        });
        return target;
	};

