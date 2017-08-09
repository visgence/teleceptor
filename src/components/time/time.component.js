import timeController from './time.controller';
import time from './time.html';
import './time.style.scss';
import 'eonasdan-bootstrap-datetimepicker';

require('./../../../node_modules/eonasdan-bootstrap-datetimepicker/build/css/bootstrap-datetimepicker.min.css');

const timecomponent = {
    template: time,
    controller: timeController,
};

export default timecomponent;
