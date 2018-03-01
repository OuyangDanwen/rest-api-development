// Registration
$(document).ready(function(){
	$('#Register_Form').on('submit', function(e){
		e.preventDefault();
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
					setCookie("uuid", response.result.token, 120); //120 minutes expiry
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

// Logout
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
					window.location.href = "http://localhost";
				}
			},
			error: function() { // When Bad Request Happens (error 400).
				alert('Error. Please Try Again.');
			}
	});
}
