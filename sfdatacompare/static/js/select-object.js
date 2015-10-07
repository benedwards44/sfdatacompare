/*
	JS logic for the Select Object page
*/


function updateModal(header, body, allow_close) {

	if (allow_close) {

		$('#progressModal .modal-header').html('<button type="button" class="close" data-dismiss="modal"><span aria-hidden="true">&times;</span><span class="sr-only">Close</span></button><h4 class="modal-title">' + header + '</h4>');
		$('#progressModal .modal-footer').html('<button type="button" class="btn btn-default" data-dismiss="modal">Close</button>');
	}

	else {

		$('#progressModal .modal-header').html('<h4 class="modal-title">' + header + '</h4>');
		$('#progressModal .modal-footer').html('');
	}

	$('#progressModal .modal-body').html(body);
}