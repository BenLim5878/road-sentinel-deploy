function initAutocomplete(map) {
    $('#loading-message').html("Loading Complete")
    $('#progress-bar-loader').css("width", "100%")
    setTimeout(() => {
        $('#app-loader').addClass('d-none')
        $('#map').addClass('fade-in-element')
        $('#map').removeClass('d-none')
        $("#place-input-sm").removeClass("d-none")
        var input = document.getElementById('place-input');
        var input_sm = document.getElementById('place-input-sm');
        var resultsContainer = document.getElementById('place-results');
        var resultsContainer_sm = document.getElementById('place-results-sm');

        var autocomplete = new google.maps.places.Autocomplete(input);
        var autocomplete_sm = new google.maps.places.Autocomplete(input_sm);

        // Listen for place changes
        autocomplete.addListener('place_changed', function () {
            // Clear previous results
            resultsContainer.innerHTML = '';

            // Get the selected place
            var place = autocomplete.getPlace();

            // Set the map's bounds to encompass the selected place's viewport (if available)
            if (place.geometry.viewport) {
                map.fitBounds(place.geometry.viewport);
            } else {
                map.setCenter(place.geometry.location);
                map.setZoom(7); // Adjust the zoom level as desired
            }
            checkViewport(map)
        })

        autocomplete_sm.addListener('place_changed', function () {
            // Clear previous results
            resultsContainer_sm.innerHTML = '';

            // Get the selected place
            var place = autocomplete_sm.getPlace();

            // Set the map's bounds to encompass the selected place's viewport (if available)
            if (place.geometry.viewport) {
                map.fitBounds(place.geometry.viewport);
            } else {
                map.setCenter(place.geometry.location);
                map.setZoom(7); // Adjust the zoom level as desired
            }
            checkViewport(map)
        })
    }, 750)
}