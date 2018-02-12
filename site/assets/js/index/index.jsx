require('jquery')
require('bootstrap')
require('react')
require('react-dom')
var React = require('react')
var ReactDOM = require('react-dom')
var IndexApp = require('./app')


var e = document.getElementById('request-id');
var requestId = e.dataset.requestId;


ReactDOM.render(
    <IndexApp 
    	requestId={requestId}
    />,
    document.getElementById('index-id')
);
