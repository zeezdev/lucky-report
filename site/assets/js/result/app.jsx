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
        reportType: json.report_type
    }
}



class ExampleChart extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      options: {
        title: 'Age vs. Weight comparison',
        hAxis: { title: 'Age', minValue: 0, maxValue: 15 },
        vAxis: { title: 'Weight', minValue: 0, maxValue: 15 },
        legend: 'none',
      },
      data: [
        ['Age', 'Weight'],
        [8, 12],
        [4, 5.5],
        [11, 14],
        [4, 5],
        [3, 3.5],
        [6.5, 7],
      ],
    };
  }
  render() {
    return (
      <Chart
        chartType="ScatterChart"
        data={this.state.data}
        options={this.state.options}
        graph_id="ScatterChart"
        width="100%"
        height="400px"
        legend_toggle
      />
    );
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
    }

    componentDidMount() {
        var self = this;
        sendAjaxRequest('GET', `/api/results/${this.props.resultId}`, {},
            function(response, textStatus, jsXHR) {
                if ('ok' in response && parseInt(response.ok) === 1) {
                    self.setState({result: deserializeResult(response.result)});
                } else {
                    console.log(`failed request /api/results/${self.props.resultId}`);
                }
            }
        );
    }


    render() {
        let result = "loading...";
        if (this.state.result != null) {
            result = (
            <div className="coll-lg-12">
                <h4 style={{color:"#666"}}>{this.state.result.query}</h4>

                <ExampleChart className="center"/>
            </div>);
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