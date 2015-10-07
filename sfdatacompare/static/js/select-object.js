/*
	JS logic for the Select Object page
*/

// Generic method to udpate the text of the modal
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

// Method to check the status of a field queyr job
function check_get_fields_job(job_id) {

	var refreshIntervalId = window.setInterval(function () {

   		$.ajax({
		    url: '/get-fields-status/' + job_id + '/',
		    type: 'get',
		    dataType: 'json',
		    success: function(resp) {

		        if (resp.status == 'Finished') {

		        	// Stop the query loop
					clearInterval(refreshIntervalId);

					// Populate fields on to page
					$('.field-select').html('SUCCESS YAY');

		        	// Hide the progress modal
					$('#progressModal').hide();

					
		        } 
		        else if (resp.status == 'Error')
		        {
					updateModal(
						'Error',
						'<div class="alert alert-danger" role="alert">There was an error querying fields for the selected object: ' + resp.error + '</div>',
						true
					);

					// Stop the query loop
					clearInterval(refreshIntervalId);
		        }
		        // Else job is still running, this will re-run shortly.
		    },
		    failure: function(resp) 
		    { 
				updateModal(
					'Error',
					'<div class="alert alert-danger" role="alert">There was an error querying fields for the selected object: ' + resp + '</div>',
					true
				);
				clearInterval(refreshIntervalId);
		    }
		});
	}, 1000);

}