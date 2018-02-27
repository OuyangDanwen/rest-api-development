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
	$('#Register_Form').on('submit', function(e){
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
					alert("Welcome.".concat($("#Username").val()));
					//window.location.href = "http://localhost";
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
