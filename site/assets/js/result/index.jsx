require('jquery')
require('bootstrap')
require('react')
require('react-dom')
var React = require('react')
var ReactDOM = require('react-dom')
var ResultApp = require('./app')


var e = document.getElementById('result-id');
var resultId = parseInt(e.dataset.id);


ReactDOM.render(
    <ResultApp />,
    document.getElementById('result')
);
