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

    var toTitleCase = function(str) {
        return str.replace(/\w\S*/g, function(txt){return txt.charAt(0).toUpperCase() + txt.substr(1);});
    };

    /**
        Takes a plain object of metadata, key/value pairs, lists, objects, and contructs html lists to display the data.

        Meant to be bound to a ul.  Otherwise take each key/value pair in the first level of the object and put them into a list.
        You can itterate over that list passing each item here to spawn multiple li elements.
    */
    ko.bindingHandlers.metadata = {

        init: function (element, valueAccessor, allBindingsAccessor, viewModel, bindingContext) {
            var metadata = ko.utils.unwrapObservable(valueAccessor());
            console.log("Binding metadata: %s" , metadata);
            var parseMetadata = function(data) {

                var html = "";

                if ($.isPlainObject(data)) {
                    $.each(data, function(key, value) {

                        if ($.isPlainObject(value) || $.isArray(value)) {
                            var ul = "<ul>"+parseMetadata(value)+"</ul>";
                            html += "<li>"+key+"</li>"+"  "+ul;
                        }
                        else
                            html += "<li>"+key+":  <span>"+value+"</span></li>";
                    });
                }
                else if($.isArray(data)) {
                    $.each(data, function(i, value) {
                        html += "<li>"+value+"</li>";
                    });
                }

                return html;
            };

            $(element).append(parseMetadata(metadata));
        }
    };


    /**
        Attaches observers on DOM nodes to watch for changes to a specified css class.
        Binding expects a plain object with the following:
        {
            elements <string>: css class selector for elements to observe.
            css <string>: css class to watch for on the observed elements.
            observable <ko observable>: Observable to store which element currently has the css class if any. null otherwise.
        }

        For this to work you must put a 'data-identifier' attr on the elements to observe.  This is what is stored in the
        observable that is passed in to identify the appropriate element.
    */
    ko.bindingHandlers.watchForCss = {
        init: function (element, valueAccessor, allBindingsAccessor, viewModel, bindingContext) {
            var data = ko.utils.unwrapObservable(valueAccessor());
            var css = data['css'];
            var eleToWatch = $(element).find(data['elements']);
            var observable = data['observable'];

            var observer = new MutationObserver(function(mutations) {
                $.each(mutations, function(i, mutation) {

                    if (mutation.type == "attributes" && mutation.attributeName == "class") {
                        if ($(mutation.target).hasClass(css))
                            observable($(mutation.target).data('identifier'));
                        else
                            observable(null);
                    }
                });
            });

            var config = { attributes: true, childList: true, characterData: true, attributeOldValue: true };
            $.each(eleToWatch, function(i, ele) {
                observer.observe(ele, config);
                if ($(ele).hasClass(css))
                    observable($(ele).data('identifier'));
            });
        }
    };

