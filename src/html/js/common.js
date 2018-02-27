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

function loadHome() {
	if (checkCookie()) {
		
		var uuid = { token: getCookie("uuid") };
		var jsonData = JSON.stringify(uuid);
		
		$.ajax({ //retrieve user info and attempt to display it.
			type: 'POST',
			url: 'http://localhost:8080/users',
			dataType: "json",
			contentType: "application/json",
			data: jsonData,
			success: function(response) { // When status (true or false) happens during registration
				if (response.status) {
					document.getElementById("welcomeHeader").innerHTML = "Welcome, " + response.result.fullname;
					document.getElementById("welcomeMsg").innerHTML = "and you are " + response.result.age + " years old.";
				} else {
					alert("Failed to retrieve info. Server down perhaps?");
				}
			},
			error: function() { // When Bad Request Happens (error 400).
				alert('Error. Please Try Again.');
			}
		});
		
		document.getElementById("welcomeHeader").innerHTML = "Welcome, ";
	} else {
		window.alert("Not Logged In...");
		window.location.href = "http://localhost";
	}	
}

function logout() {
	var uuid = { token: getCookie("uuid") };
	var jsonData = JSON.stringify(uuid);
	
	$.ajax({
			type: 'POST',
			url: 'http://localhost:8080/users/expire',
			dataType: "json",
			contentType: "application/json",
			data: jsonData,
			success: function(response) { // When status (true or false) happens during registration
				if (response.status) {
					destroyCookie();
					alert("Logout Successful.");
					window.location.href = "http://localhost";
				} else {
					alert("Failed to logout. Perhaps token already terminated previously?");
					window.location.href = "http://localhost";
				}
			},
			error: function() { // When Bad Request Happens (error 400).
				alert('Error. Please Try Again.');
			}
	});
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

// End of Javascript Cookie functions


/* AJAX Codes */

// Registration
$(document).ready(function(){
	$('#Register_Form').on('submit', function(e){
		e.preventDefault();
		// TODO: Field Validation
		
		// Passwords Matching
		if ($("#Password").val() != $("#CfmPassword").val()) {
			alert("Passwords do not match.");
			return;
		}
				
		var formData = {
			username: $("#Username").val(), 
			password: $("#Password").val(), 
			fullname: $("#Fullname").val(),
			age: $("#Age").val()
		};
		var jsonData = JSON.stringify(formData);
		$.ajax({
			type: 'POST',
			url: 'http://localhost:8080/users/register',
			dataType: "json",
			contentType: "application/json",
			data: jsonData,
			success: function(response) { // When status (true or false) happens during registration
				if (response.status) {
					alert("Registration Successful.");
					window.location.href = "http://localhost";
				} else {
					alert(response.error);
				}
			},
			error: function() { // When Bad Request Happens (error 400).
				alert('Error. Please Try Again.');
			}
		});
	});
});

// Login
$(document).ready(function(){
	$('#Login_Form').on('submit', function(e){
		e.preventDefault();
		
		var formData = {
			username: $("#Username").val(), 
			password: $("#Password").val()
		};
		
		var jsonData = JSON.stringify(formData);
		$.ajax({
			type: 'POST',
			url: 'http://localhost:8080/users/authenticate',
			dataType: "json",
			contentType: "application/json",
			data: jsonData,
			success: function(response) { // When status (true or false) happens during login
				if (response.status) {
					alert("UUID Value (Check with Cookie Value): " + response.result.token); // TO REMOVE THIS. FOR DEBUG PURPOSES ONLY
					setCookie("uuid", response.result.token, 30); //30 minutes expiry
					window.location.href = "http://localhost/home.html";
				} else {
					alert("Invalid Username or Password.");
				}
			},
			error: function() { // When Bad Request Happens (error 400).
				alert('Error. Please Try Again.');
			}
		});
	});
});
