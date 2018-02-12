import Cookie from 'js-cookie'

/**
* done <function(response, textStatus, jsXHR) {...}>: success processing;
*/
function sendAjaxRequest(reqType, url, data, done, always, fail, timeout) {
    var _done = function() {};
    var _always = function(response) {
        /*if (response.status === 301 && 'redirect_url' in response.responseJSON) {
            window.location.href = response.responseJSON.redirect_url; 
        }*/
    };
    var _fail = function(jqXHR,status,err){
        alert('Error (' + status + '): ' + err + '\n' + jqXHR.responseText);
    };
    var _reqType = reqType || 'POST'
    var _timeout = 60000;

    if (typeof done !== 'undefined') _done = done;
    if (typeof always !== 'undefined') _always = always;
    if (typeof fail !== 'undefined') _fail = fail;
    if (typeof reqType !== 'undefined') _reqType = reqType;
    if (typeof timeout !== 'undefined') _timeout = timeout;

    // var csrftoken = $('input[name=csrfmiddlewaretoken]').val();
    // var csrftoken = $.cookie('csrftoken');
    var csrftoken = Cookie.get('csrftoken');
    let headers = { 'X-CSRFToken': csrftoken };
//	if (reqType == 'DELETE') {
//		_reqType = 'POST';
//		headers['X_METHODOVERRIDE'] = 'DELETE';
//	} else if (reqType == 'PUT') {
//		_reqType = 'POST';
//		headers['X_METHODOVERRIDE'] = 'PUT';
//	}
    $.ajax({
        url: url,
		headers: headers,
        data: data,
        cache: false,
        type: _reqType,
        // contentType: "application/json; charset=utf-8",
        // dataType: "json",
        timeout: _timeout,
    }).always(_always).done(_done).fail(_fail);
};


module.exports = {
    sendAjaxRequest: sendAjaxRequest
}
