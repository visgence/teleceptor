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

(function($) {
	"use strict";

	var UPDATE = 1,
	    REPLACE = 2;

	var methods = [UPDATE, REPLACE];
	var defaultMethod = UPDATE;


	function updateRoute(routeObj, reload) {
		var params = updateParams(window.location.search, routeObj, UPDATE);
		var href = window.location.pathname + params;

		if (reload === true)
			window.location.href = href;
		else
			History.pushState(null, "", href);
	}

	function updateParams(params, obj, method) {

		if (typeof(params) !== "string" || params.trim() === "")
			params = window.location.search;

		if (!$.isPlainObject(obj) || $.isEmptyObject(obj))
			return params;

		var method = $.inArray(method, methods) !== -1 ? method : defaultMethod;
		var paramObj = deparam(params);

		var newParam = "";
		switch(method) {

			case UPDATE:
				newParam = "?"+$.param(updateObject(paramObj, obj));
				break;

			case REPLACE:
				newParam = "?"+$.param(obj);
				break;

			default:
				throw("Error updating params with invalid method %s", method);
		}

		return newParam;
	}

	function paramState() {
		return deparams(window.location.search);
	}

	function deparam(params) {
		var paramsObj = {}

		if (typeof(params) !== "string" || params.trim() === "")
			return paramsObj;

		var rawParams = params.split("?")[1].split("&");

		$.each(rawParams, function(i, param) {
			var keyVal = param.split("=");
			paramsObj[keyVal[0]] = keyVal[1];
		});

		return paramsObj;
	}

	function updateObject(obj, data) {
		if (!$.isPlainObject(obj))
			throw("Error updating object.  %s is not a plain object.", obj);

		if (!$.isPlainObject(data) || $.isEmptyObject(data))
			return obj;

		$.each(data, function(key, value) {
			obj[key] = value;

			if (value === null)
				delete obj[key];
		});

		return obj;
	}


	$.fn.updateParams = updateParams;
	$.fn.deparam = deparam;
	$.fn.updateObject = updateObject;
	$.fn.updateRoute = updateRoute;
	$.fn.paramState = paramState;

}(jQuery))
