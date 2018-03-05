var diaryEntriesId = {};

$(document).ready(function() {

	$('#sidebar').load("sidebar.html");

	var group = getUrlParameter("group");
	setPageHeader(group);
	populateTable(group);
	setButtonOnclick(group);

	$('#entry-details-dialog').dialog({
		width: 800,
		autoOpen: false,
		modal: true,
		title: 'Diary Entry',
		buttons: {
			Close: function() {
				$(this).dialog('close');
			}
		}
	});

	$('#entry-details-addnl-dialog').dialog({
		width: 800,
		autoOpen: false,
		modal: true,
		title: 'Diary Entry',
		buttons: {
			Save: function() {
				var formData = {
					"token": getCookie("uuid"),
					"id": $('#entry-text-addnl').val(),
					"public": $('#viewable-public-addnl').prop('checked')
				};
				var jsonData = JSON.stringify(formData);

				$.ajax({
					type: "POST",
					url: baseURL + ':8080/diary/permission',
					dataType: "json",
					contentType: "application/json",
					data: jsonData,
					success: function(response) {
						if (response.status) {
							alert("Permissions updated");
							window.location.reload();
						} else {
							alert(response.error);
						}
					},
					error: function() {
						alert('Error. Please try again.');
					}
				});

				$(this).dialog('close');
			},
			Close: function() {
				$(this).dialog('close');
			}
		}
	});

});

function setPageHeader(group) {
	if (group === "public") {
		$('#page-header').text("View public entries");
	}
}

function populateTable(group) {
	if (group === "self") {
		var formData = { token: getCookie("uuid") };                            
		var jsonData = JSON.stringify(formData);

		$.ajax({
			type: "POST",
			url: baseURL + ':8080/diary',
			dataType: "json",
			contentType: "application/json",
			data: jsonData,
			success: function(response) {
				if (response.status) {
					parseToHtml(response.result, group);
				} else {
					alert(response.error);
				}
			},
			error: function() {
				alert('Error. Please try again.');
			}
		});
	} else if (group === "public") {
		$.ajax({
			type: "GET",
			url: baseURL + ':8080/diary',
			success: function(response) {
				if (response.status) {
					parseToHtml(response.result, group);
				} else {
					alert(response.error);
				}
			},
			error: function() {
				alert('Error. Please try again.');
			}
		});   
	}
}

function setButtonOnclick(group) {
	$(document).on('click', '#btnView', function() {
		var entryDetails = diaryEntriesId[$(this).val()];
		if (group === "self") {
			if (entryDetails.public) {
				$('#viewable-public-addnl').prop('checked', true);
			} else {
				$('#viewable-public-addnl').prop('checked', false);
			}
			$('#entry-text-addnl').text(entryDetails.text);
			$('#entry-text-addnl').val($(this).val());
			$('#entry-details-addnl-dialog').dialog('open');
		} else if (group === "public") {
			$('#entry-text').text(entryDetails.text);
			$('#entry-details-dialog').dialog('open');
		}
	});
	
	$(document).on('click', '#btnDelete', function() {
		var btnValue = $(this).val();
		$('<div></div>').appendTo('body')
			.html('<div><p>Are you sure you want to delete this entry?</p></div>')
			.dialog({
				modal: true, title: 'Confirm Entry Deletion', zIndex: 10000, autoOpen: true,
				width: 'auto', resizable: false,
				buttons: {
					Yes: function () {
						var data = { 
							token: getCookie("uuid"),
							id: btnValue
						};
						var jsonData = JSON.stringify(data);

						$.ajax({
							type: 'POST',
							url: baseURL + ':8080/diary/delete',
							dataType: "json",
							contentType: "application/json",
							data: jsonData,
							success: function(response) {
								if (response.status) {
									alert("Diary entry deleted.");
									window.location.reload();
								} else {
									alert(response.error);
								}
							},
							error: function() {
								alert('Error. Please Try Again.');
							}
						});

						$(this).dialog('close');
					},
					No: function () {
						$(this).dialog('close');
					}
				},
				close: function (event, ui) {
					$(this).remove();
				}
			})
	});
}

function parseToHtml(entries, group) {
	var html = "";
	var count = 1;

	for (var i in entries) {
		diaryEntriesId[entries[i].id] = entries[i];

		html += "<tr>";
		html += "<td>" + count + "</td>";
		html += "<td>" + DOMPurify.sanitize(entries[i].title) + "</td>";
		html += "<td>" + entries[i].author + "</td>";
		html += "<td>" + entries[i].publish_date + "</td>";
		html += "<td><button class='btn btn-circle' id='btnView' title='View Text' value='" + entries[i].id + "'><i class='far fa-file-alt'></i></button>";
		if (group === "self") {
			html += "<button class='btn btn-circle' id='btnDelete' title='Delete' value='" + entries[i].id + "'><i class='far fa-trash-alt'></i></button></td>";
		} else  {
			html += "</td>";
		}
		html += "</tr>";
		count++;
	}

	$('#table-entries > tbody').html(html);
}
