/*
	Angular controller for all the Compare Objects results page
*/

var compareResultsApp = angular.module("compareResultsApp", ['ngRoute', 'ngResource']);

compareResultsApp.controller("CompareResultsController", function($scope) 
{

	// On initation of controller
    $scope.init = function(job_id, object_id)
    {
        // Job ID passed through from view
        $scope.job_id = job_id;

        // Object ID passed from the view
        $scope.object_id = object_id

        // Array of unmatched records to display
        $scope.records = [];

        // Enable tooltips
		$('[data-toggle="tooltip"]').tooltip();
    }

    // When the compare button is checked.
    $scope.rerunJob = function()
    {
    	// Execute AJAX call
    	$http(
        {
            method: 'GET',
            url: '/compare-data/' + $scope.job_id + '/' + $scope.object_id + '/',
        }).
        success(function(data, status) 
        {
            // Redirect to the loading page
            window.location = data;
        }).
        error(function(data, status) 
        {
            // Return error in a modal
            updateModal(
                'Error Executing Data Compare',
                '<div class="alert alert-danger" role="alert">There was an error executing the data compare job.' + data + '</div>',
                true
            );

            // Close the modal
            $('#progressModal').modal();
        });

    }

});
