/*
	Angular controller for all the Select Object page
*/

var selectObjectsApp = angular.module("selectObjectsApp", ['ngRoute', 'ngResource']);

selectObjectsApp.controller("SelectObjectsController", function($scope, $http, $q) 
{

	// On initation of controller
    $scope.init = function(job_id)
    {
    	$('#field-select').hide();

        // Job ID passed through from view
        $scope.job_id = job_id;

        // Array of fields for the page
        $scope.fields = [];
    }

    // When an object selection is changed
    $scope.objectChange = function()
    {

    	// Hide the selection div
        $('#field-select').hide('slow');

    	// Clear the fields
    	$scope.fields = [];

        // If an object has been selected
    	if ($scope.objectId != '')
        {
        	// Clear the fields
        	$scope.fields = [];

        	// Query for objects
        	updateModal(
				'Querying fields.',
				'<div>Querying both Orgs to determine matching fields for the selected object.</div><div class="progress"><div class="progress-bar progress-bar-warning progress-bar-striped active" role="progressbar" aria-valuenow="100" aria-valuemin="0" aria-valuemax="100" style="width: 100%"></div></div>',
				false
			);

			// Launch the loading modal
			$('#progressModal').modal();

			// Execute callout to get the fields for the object
			$http(
            {
                method: 'GET',
                url: '/get-fields/' + $scope.job_id + '/' + $scope.objectId + '/',
                headers: {
                    'Content-Type': 'application/json'
                }
            }).
            success(function(data, status) 
            {
            	// If there was an error in the callout
                if (data.error) 
                {
                    updateModal(
						'Error',
						'<div class="alert alert-danger" role="alert">There was an error getting fields for the object: ' + data.errorMessage + '</div>',
						true
					);
                }
                else
                {   
                    // Loop through resulting array
                    for (var i = 0; i < data.length; i++)
                    {
                        // Create a new layout
                        $scope.field = {
                            'id': data[i].id,
							'label': data[i].label,
							'api_name': data[i].api_name,
							'type': data[i].type,
							'checked': false
                        };

                        // Push to array
                        $scope.fields.push($scope.field);
                    }

                    // Show table and hide message
                    $('#field-select').show('slow');

                    // Close the modal
                    $('#progressModal').modal('hide');

                }   

            }).
            error(function(data, status) 
            {
                updateModal(
					'Error',
					'<div class="alert alert-danger" role="alert">There was an error getting fields for the object: ' + data.error + '</div>',
					true
				);
            });

        }
    }

    // When the checkall checkbox is checked
    $scope.checkAllChange = function()
    {
    	angular.forEach($scope.fields, function (field) {
            field.checked = $scope.checkAll;
        });
    }

    // When the compare button is checked.
    $scope.compareData = function()
    {
    	// The list of fields to compare
    	fields_to_compare = [];

    	// Iterate over the fields
    	angular.forEach($scope.fields, function (field) {
 
 			// If the field is checked, add it to the list
    		if (field.checked) {

    			fields_to_compare.push(field.api_name);
    		}
    	});

    	// Execute logic to being the data compare job
    	if (fields_to_compare.length > 0) {

    		alert('GO.');

    	}
    	// No fields are checked, return an error
    	else {

    		updateModal(
				'No Fields Selected',
				'<div class="alert alert-danger" role="alert">No fields selected. Please choose at least 1 field to compare on.</div>',
				true
			);

    		// Close the modal
            $('#progressModal').modal();
    	}
    }
});