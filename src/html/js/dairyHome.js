function loadHome() {
	if (checkCookie()) {
		
		var uuid = { token: getCookie("uuid") };
		var jsonData = JSON.stringify(uuid);
		
		$.ajax({ //retrieve user info and attempt to display it.
			type: 'POST',
			url: baseURL + ':8080/users',
			dataType: "json",
			contentType: "application/json",
			data: jsonData,
			success: function(response) {
				if (response.status) {
					document.getElementById("welcomeHeader").innerHTML = "Welcome, " + response.result.fullname;
					document.getElementById("welcomeMsg").innerHTML = "and you are " + response.result.age + " years old.";
				} else {
					window.alert("Please Log In Again.");
					window.location.href = "index.html";
				}
			},
			error: function() { // When Bad Request Happens (error 400).
				window.alert('Error. Please Try Again.');
				window.location.href = "index.html";
			}
		});
		
		document.getElementById("welcomeHeader").innerHTML = "Welcome, ";
	} else {
		window.alert("Not Logged In...");
		window.location.href = "index.html";
	}	
}

$(function() {
    $('#sidebar').load("sidebar.html");
});
