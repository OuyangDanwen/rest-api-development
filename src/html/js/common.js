// Store Host Name Here.
var baseURL = "http://" + document.location.hostname;

function getUrlParameter(sParam) {
    var sPageURL = window.location.search.substring(1);
    var sURLVariables = sPageURL.split('&');
    for (var i = 0; i < sURLVariables.length; i++) {
        var sParameterName = sURLVariables[i].split('=');
        if (sParameterName[0] == sParam) {
            return sParameterName[1];
        }
    }
}

// Start Javascript Cookie Functions.. Insecure as f*ck.
// Taken from https://www.w3schools.com/js/js_cookies.asp

function setCookie(cname, cvalue, exdays) {
	var d = new Date();
    d.setTime(d.getTime() + (exdays * 60 * 1000));
    var expires = "expires="+d.toUTCString();
    document.cookie = cname + "=" + cvalue + ";" + expires + ";path=/";
}

function getCookie(cname) { //returns cookie value
    var name = cname + "=";
    var decodedCookie = decodeURIComponent(document.cookie);
    var ca = decodedCookie.split(';');
    for(var i = 0; i < ca.length; i++) {
        var c = ca[i];
        while (c.charAt(0) == ' ') {
            c = c.substring(1);
        }
        if (c.indexOf(name) == 0) {
            return c.substring(name.length, c.length);
        }
    }
    return "";
}

function checkCookie() {
    var user = getCookie("uuid");
    if (user == "") { // no uuid cookie detected
       	return false;
    } else {
		return true;
	}
}	

function destroyCookie() {	
	document.cookie = "uuid=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
}

// Determine whether cookie is valid by using https://cs5331-assignments.github.io/rest-api-development/#users-retrieve-user-information-post
function isCookieValid() {
	if (!checkCookie()) {
		window.alert("Not Logged In...");
		window.location.href = "index.html";
		return;
	}
	
	var uuid = { token: getCookie("uuid") };
	var jsonData = JSON.stringify(uuid);
	
	$.ajax({
		type: 'POST',
		url: baseURL + ':8080/users',
		dataType: "json",
		contentType: "application/json",
		data: jsonData,
		success: function(response) {
			if (!response.status) {
				window.alert("Please Log In Again.");
				window.location.href = "index.html";
			}
		},
		error: function() { // When Bad Request Happens (error 400).
			window.alert('Error. Please Try Again.');
			window.location.href = "index.html";
		}
	});
}

// End of Javascript Cookie functions
