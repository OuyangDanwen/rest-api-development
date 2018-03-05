$(document).ready(function() {
	$('#sidebar').load("sidebar.html");

	$('#form-diary-entry .form-group button').click(function(e) {
		e.preventDefault();

		var id = $(this).attr("id");
		if (id === "btnCancel") {
			location.href = "home.html";
		} else if (id === "btnSave") {
			var titleSanitised = DOMPurify.sanitize($('#title').val());
			var entryTextSanitised = DOMPurify.sanitize($('#entryText').val());

			var formData = {
				token: getCookie("uuid"),
				title: titleSanitised,
				public: $("#viewablePublic").prop('checked'), 
				text: entryTextSanitised
			};
			var jsonData = JSON.stringify(formData);

			$.ajax({
				type: 'POST',
				url: baseURL + ':8080/diary/create',
				dataType: "json",
				contentType: "application/json",
				data: jsonData,
				success: function(response) {
					if (response.status) {
						alert("Diary entry created.");
						window.location.href = "viewentries.html?group=self";
					} else {
						alert(response.error);
					}
				},
				error: function() {
					alert('Error. Please Try Again.');
				}
			});
		}
	});
});
