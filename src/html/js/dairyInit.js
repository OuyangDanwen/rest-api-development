// Meta
function Meta() {
	$.ajax({
		type: "GET",
		url: baseURL + ':8080/meta/members',
		success: function(response) {
			if (response.status) {
				alert("Success.\n\nTeam Members:\n" + response.result);
			} else {
				alert("Looks like API is down.");
			}
		},
		error: function() {
			alert("Looks like API is down.");
		}
	});  
}

// Registration
$(document).ready(function(){
	$('#Register_Form').on('submit', function(e){
		e.preventDefault();
		var passwordSanitised = DOMPurify.sanitize($('#Password').val());
		var cfmPasswordSanitised = DOMPurify.sanitize($("#CfmPassword").val());
		var usernameSanitised = DOMPurify.sanitize($("#Username").val());
		var fullnameSanitised = DOMPurify.sanitize($("#Fullname").val());
		// Partial Validation Implemented, Sufficient For This Assignment
		
		// Age Integer Verification
		if (!Number.isInteger(parseInt($("#Age").val()))) {
			alert("Invalid Age.");
			return;
		}
		
		if ($("#Age").val() < 0 || $("#Age").val() > 125) {
			alert("Are you too young or too old? Because that age is impossible on Earth!1!1!1");
			return;
		}
		
		// Passwords Matching
		if (passwordSanitised != cfmPasswordSanitised) {
			alert("Passwords do not match.");
			return;
		}
				
		var formData = {
			username: usernameSanitised, 
			password: passwordSanitised, 
			fullname: fullnameSanitised,
			age: $("#Age").val()
		};
		var jsonData = JSON.stringify(formData);
		$.ajax({
			type: 'POST',
			url: baseURL + ':8080/users/register',
			dataType: "json",
			contentType: "application/json",
			data: jsonData,
			success: function(response) { // When status (true or false) happens during registration
				if (response.status) {
					alert("Registration Successful.");
					window.location.href = "index.html";
				} else {
					alert(response.error);
				}
			},
			error: function() { // When Bad Request Happens (error 400).
				alert('Error. Please Try Again.');
				window.location.href = "register.html";
			}
		});
	});
});

// Login
$(document).ready(function(){
	$('#Login_Form').on('submit', function(e){
		e.preventDefault();
		var usernameSanitised = DOMPurify.sanitize($("#Username").val());
		var passwordSanitised = DOMPurify.sanitize($('#Password').val());
		
		var formData = {
			username: usernameSanitised,
			password: passwordSanitised
		};
		
		var jsonData = JSON.stringify(formData);
		$.ajax({
			type: 'POST',
			url: baseURL + ':8080/users/authenticate',
			dataType: "json",
			contentType: "application/json",
			data: jsonData,
			success: function(response) { // When status (true or false) happens during login
				if (response.status) {
					setCookie("uuid", response.result.token, 120); //120 minutes expiry
					window.location.href = "home.html";
				} else {
					alert("Invalid Username or Password.");
				}
			},
			error: function() { // When Bad Request Happens (error 400).
				alert('Error. Please Try Again.');
				window.location.href = "index.html";
			}
		});
	});
});

// Logout
function logout() {
	var uuid = { token: getCookie("uuid") };
	var jsonData = JSON.stringify(uuid);
	
	$.ajax({
			type: 'POST',
			url: baseURL + ':8080/users/expire',
			dataType: "json",
			contentType: "application/json",
			data: jsonData,
			success: function(response) { // When status (true or false) happens during registration
				if (response.status) {
					destroyCookie();
					alert("Logout Successful.");
					window.location.href = "index.html";
				} else {
					window.location.href = "index.html";
				}
			},
			error: function() { // When Bad Request Happens (error 400).
				alert('Error. Redirecting...');
				window.location.href = "index.html";
			}
	});
}
