require('jquery')
require('bootstrap')
require('react')
require('react-dom')
var React = require('react')
var ReactDOM = require('react-dom')
var IndexApp = require('./app')


var e = document.getElementById('request-id');
var requestId = e.dataset.requestId;
var requestText = e.dataset.requestText;


ReactDOM.render(
    <IndexApp 
    	requestId={requestId}
    	requestText={requestText}
    />,
    document.getElementById('index-id')
);
