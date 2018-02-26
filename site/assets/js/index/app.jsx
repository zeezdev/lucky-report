import React from 'react';
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



/**
* props:
*   key <int>: key
*   resultId <int>: ???
*   displayResult <str>: ???
*   reportType <int>: ???
*/
class ResultItem extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
        }
        this.reportType2ImgSource = this.reportType2ImgSource.bind(this);
    }

    reportType2ImgSource(reportType) {
        return {
            1: 'icons8-data-sheet-50.png',
            2: 'icons8-combo-chart-50.png',
            3: 'icons8-doughnut-chart-50.png'
        }[reportType];
    }

    render() {
        let imgSource = "/static/img/" + this.reportType2ImgSource(this.props.reportType);
        return (
            <div className="panel panel-default">
                <div className="panel-body" data-id={this.props.resultId} style={{padding:"8px 16px"}}>
                    <a
                        href={"/results/?id=" + this.props.resultId}
                        target="_blank"
                    >
                    <table>
                        <tbody>
                            <tr>
                                <td width="100%">
                                    {this.props.displayResult}
                                </td>
                                <td width="50px">
                                    <img src={imgSource} />
                                </td>
                            </tr>
                        </tbody>
                        </table>
                    </a>
                </div>
            </div>
        )
    }
}


class ResultsList extends React.Component {
    constructor(props) {
        super(props);
    }

    render() {
        return (
            <div>
                {
                    this.props.results.map((obj, index) => {
                        return <ResultItem
                            key={index}
                            resultId={obj.id}
                            displayResult={obj.query}
                            reportType={obj.reportType}
                        />
                    })
                }
            </div>
        )
    }
}

/**
* props:
*   requestId: null or <int>
*   requestText: null or <str>
*/
class IndexApp extends React.Component {
        constructor(props) {
            super(props);
            this.state = {
                queryValue: props.requestText || "",
                results: []
            }
            this.sendRequest.bind(this);
        }

        componentDidMount() {
            if (this.props.requestId != "") {
                var self = this;
                sendAjaxRequest('GET', '/api/results', {'request_id': this.props.requestId},
                    function(response, textStatus, jsXHR) {
                        if ('ok' in response && parseInt(response.ok) === 1) {
                            let results = [];
                            for (let result of response.results) {
                                results.push(deserializeResult(result));
                            }
                            self.setState({results: results});
                        }
                    }                    
                );
            }
        }

        resetFound() {

        }

        handleQueryOnChange(e) {
            this.setState({queryValue: e.target.value});
        }

        sendRequest(request) {
            this.resetFound();
            sendAjaxRequest('GET', '/api/request', {'request': request},
                function(response, textStatus, jsXHR) {
                    if ('ok' in response && parseInt(response.ok) === 1) {
                        if ('request_id' in response) {
                            var requestId = parseInt(response.request_id);
                            window.location.assign('/?request_id=' + requestId);
                        }
                    }
                }
            );
        }

        handleQueryOnKeyPress(e) {
            if (e.charCode == 13) { // ENTER
                this.sendRequest(this.state.queryValue);
            }
        }

        handleQueryOnClick(e) {
            this.sendRequest(this.state.queryValue);
        }

        render() {
            let header = "";
            let additionalClassNames = "";
            if (this.props.requestId != "") {
                header = <h2 className="lr-logo">Lucky Report</h2>;
                // additionalClassNames = "landing-post";
            } else {
                header = (
                    <div>
                        <h1 className="lr-logo">
                            Lucky Report
                            <img src="/static/img/dice.png" style={{width:"92px", margin:"16px"}} />
                        </h1>
                    </div>
                    );
                additionalClassNames = "landing";
            }

            return (
                <div className={additionalClassNames}>
                  {header}
                  <div className="row">
                    <div className="col-lg-12" style={{maxWidth:"600px"}}>
                        <div className="input-group" style={{margin: "16px 0px"}}>
                            <input
                                type={"text"}
                                style={{width:"100"}}
                                className="form-control"
                                value={this.state.queryValue}
                                onChange={this.handleQueryOnChange.bind(this)}
                                onKeyPress={this.handleQueryOnKeyPress.bind(this)}
                                placeholder={"Please enter your request"}
                                />
                            <span className="input-group-btn">
                                <button
                                    className="btn btn-success"
                                    type="button"
                                    onClick={this.handleQueryOnClick.bind(this)}
                                >I'm feeling lucky!</button>
                            </span>
                        </div>
                    </div>
                    <div className="col-lg-12">
                        <ResultsList results={this.state.results}/>
                    </div>
                  </div>
                </div>
            )
        }
}


module.exports = IndexApp;