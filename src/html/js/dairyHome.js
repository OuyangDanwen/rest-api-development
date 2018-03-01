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

$(function() {
    $('#sidebar').load("sidebar.html");
});
