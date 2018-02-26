//import { Chart } from 'react-google-charts';
import React from 'react';
// const Chart = ReactGoogleCharts.default.Chart
var Chart = require('../react-google-charts.min');
var sendAjaxRequest = require('../ajax').sendAjaxRequest;


var deserializeResult = function(json) {
    return {
        id: json.id,
        requestId: json.request_id,
        query: json.query,
        rate: json.rate,
        reportType: json.report_type,
    }
}


/**
* props:
*   graphName <str>: ???
*   data <Object>: ???
*   columns <Array>: ???
*   title <st>: ???
*   
*/
let BaseGoogleChart = (superclass) => class extends superclass{
    constructor(props) {
        super(props);
        this.drawCharts = this.drawCharts.bind(this);
    }

    render() {
        return (
            <div 
                id={this.props.graphName} 
                style={{height: "600px", padding: "16px 0px"}} 
            />
        )
    }

    componentDidMount(){
        this.drawCharts();
    }

    componentDidUpdate(){
        this.drawCharts();
    }

    drawCharts() { }

}

class GoogleLineChart extends BaseGoogleChart(React.Component) {
    drawCharts(){
        var raw_data = [];
        raw_data.push(this.props.columns);
        for (var d of this.props.data) {
            raw_data.push(d);
        }

        var data = google.visualization.arrayToDataTable(raw_data);
        var options = { title: this.props.title };

        var chart = new google.visualization.LineChart(document.getElementById(this.props.graphName));
        chart.draw(data, options);
    }
}

class GoogleTableChart extends BaseGoogleChart(React.Component) {
    drawCharts(){
        // var data = google.visualization.arrayToDataTable(this.props.data);
        var data = new google.visualization.DataTable();
        for (var column of this.props.columns) {
            data.addColumn("string", column.toString());
        }
        var rows = this.props.data.slice(); // copy
        for (let i = 0; i < rows.length; i++) {
            for (let j = 0; j < rows[i].length; j++) {
                if (rows[i][j] == null) {
                    rows[i][j] = '';
                } else {
                    rows[i][j] = rows[i][j].toString();
                }
            }
        }
        data.addRows(rows);

        var options = {
            showRowNumber: true, 
            width: '100%',
            height: '100%',
            title: this.props.title,
        };

        var table = new google.visualization.Table(document.getElementById(this.props.graphName));
        table.draw(data, options);
    }
}

class GooglePieChart extends BaseGoogleChart(React.Component) {
    drawCharts(){
        var raw_data = [];
        raw_data.push(this.props.columns);
        for (var d of this.props.data) {
            raw_data.push([d[0].toString(), d[1]]);
        }

        var data = google.visualization.arrayToDataTable(raw_data);
        var options = {
            title: this.props.title,
        };

        var chart = new google.visualization.PieChart(document.getElementById(this.props.graphName));
        chart.draw(data, options);
    }
}


/**
* props:
*   resultId <int>: db identifier of result for display
*/
class ResultApp extends React.Component {

    constructor(props) {
        super(props);
        this.state = {
            result: null
        };
        this.renderTable = this.renderTable.bind(this);
        this.renderGraph = this.renderGraph.bind(this);
        this.renderPie = this.renderPie.bind(this);
    }

    componentDidMount() {
        var self = this;
        sendAjaxRequest('GET', `/api/results/${this.props.resultId}`, {},
            function(response, textStatus, jsXHR) {
                if ('ok' in response && parseInt(response.ok) === 1) {
                    self.setState({
                        result: deserializeResult(response.result),
                        data: response.data,
                        columns: response.columns
                    });
                } else {
                    console.log(`failed request /api/results/${self.props.resultId}`);
                }
            }
        );
    }

    renderTable() {
        return (
            <GoogleTableChart 
                graphName="Test"
                title={this.state.result.query}
                data={this.state.data}
                columns={this.state.columns}
            />
        )
    }    

    renderGraph() {
        return (
            <GoogleLineChart 
                graphName="Test"
                title={this.state.result.query}
                data={this.state.data}
                columns={this.state.columns}
            />
        )
    }    


    renderPie() {
        return (
            <GooglePieChart 
                graphName="Test"
                title={this.state.result.query}
                data={this.state.data}
                columns={this.state.columns}
            />
        )
    }

    render() {
        let result = "loading...";

        if (this.state.result != null) {
            let report = this.renderTable(); // table by-default
            if (this.state.result.reportType == 2) { // graph 
                report = this.renderGraph();
            } else if (this.state.result.reportType == 3) { // pie
                report = this.renderPie();
            }

            result = (
                <div className="coll-lg-12">
                    <h4 style={{color:"#666"}}>{this.state.result.query}</h4>
                    {report}
                </div>
            );
        }

        return (
            <div>
                <h2>Report Result</h2>
                <div className="row">
                    {result}
                </div>
            </div>
        )
    }

}


module.exports = ResultApp;