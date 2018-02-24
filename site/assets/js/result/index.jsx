require('jquery')
require('bootstrap')
require('react')
require('react-dom')
var React = require('react')
var ReactDOM = require('react-dom')
var ResultApp = require('./app')


var e = document.getElementById('result-id');
var resultId = parseInt(e.dataset.id);


var drawResult = function() {
	ReactDOM.render(
	    <ResultApp
	        resultId={resultId}
	    />,
	    document.getElementById('result')
	);
};

google.charts.load('current', {packages: ['corechart', 'table']});
google.charts.setOnLoadCallback(drawResult); // render after page loading
