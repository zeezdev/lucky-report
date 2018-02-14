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
    }

    render() {
        return (
            <div className="panel panel-default">
                <div className="panel-body" data-id={this.props.resultId}>
                    <a
                        href={"/results/?id=" + this.props.resultId}
                        target="_blank"
                    >
                    {this.props.displayResult}
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
*/
class IndexApp extends React.Component {
        constructor(props) {
            super(props);
            this.state = {
                queryValue: "",
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
            return (
                <div>
                  <h1 className="lr-logo">Lucky Report</h1>
                  <div className="row">
                    <div className="col-lg-12">
                        <div className="input-group" style={{margin: "16px 0px"}}>
                            <input
                                type={"text"}
                                style={{width:"100%"}}
                                className="form-control"
                                value={this.state.findWordValue}
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