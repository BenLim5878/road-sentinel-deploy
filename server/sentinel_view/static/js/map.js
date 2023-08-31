var map
var eastMalaysiaMarker
var westMalaysiaMarker
var stateMalaysiaMarker = []
var annotateMarker = []
var showCountryStats = true
var showStateStats = false
var isZoomChangedProcessing = Promise.resolve()
var tempImageAnnotationID
const throttleDelay = 100

function initMap() {
    $('#loading-message').html("Loading System Configuration...")
    $('#progress-bar-loader').css("width", "25%")
    $.ajax({
        url: '/api/setting',
        type: 'GET',
        success: function (setting) {
            $('#loading-message').html("Fetching Map Configuration...")
            $('#progress-bar-loader').css("width", "75%")
            // Init map
            console.log(setting)
            map = new google.maps.Map(document.getElementById('map'), {
                center: { lat: 4.228226, lng: 109.174870 },
                mapTypeControl: false,
                zoom: setting.MAP_INITIAL_ZOOM_LEVEL,
                minZoom: setting.MAP_MINIMUM_ZOOM_LEVEL, // Set the minimum allowed zoom level
                maxZoom: setting.MAP_MAXIMUM_ZOOM_LEVEL, // Set the maximum allowed zoom level
            },);
            google.maps.event.addListener(map, 'drag', limitEventsPerSecond(function () {
                checkViewport(map)
            }, 1));

            google.maps.event.addListener(map, 'zoom_changed', async function () {
                await isZoomChangedProcessing

                try {
                    isZoomChangedProcessing = (async () => {
                        closePanel()
                        checkViewport(map)
                        await delay(throttleDelay)
                    })();
                } catch (error) {
                    console.log('Error occured during event processing:', error)
                }
            });

            google.maps.event.addListenerOnce(map, 'idle', function () {
            })

            google.maps.event.addListener(map.getStreetView(), 'visible_changed', function () {
                closePanel()
                if (map.getStreetView().getVisible()) {
                    $("#place-input-sm").addClass("d-none")
                } else {
                    $("#place-input-sm").removeClass("d-none")
                }

            });

            $('#loading-message').html("Generating Map Components...")
            $('#progress-bar-loader').css("width", "99%")
            initAutocomplete(map)

            getCountryData((response) => {
                addEastWestMalaysiaMarker(map, response["east_malaysia_total_potholes"], response["west_malaysia_total_potholes"])
            })
        },
    });
}

function delay(ms) {
    return new Promise(resolve => setTimeout(resolve, ms))
}

function checkViewport(map_data) {
    var bounds = map_data.getBounds();
    var sw = bounds.getSouthWest();
    var ne = bounds.getNorthEast();
    var westMalaysiaBounds = new google.maps.LatLngBounds(
        new google.maps.LatLng(1.157, 99.641),
        new google.maps.LatLng(7.521, 102.138)
    );

    var eastMalaysiaBounds = new google.maps.LatLngBounds(
        new google.maps.LatLng(0.842, 109.595),
        new google.maps.LatLng(7.529, 119.618)
    );

    var westMalaysiaVisible = westMalaysiaBounds.intersects(bounds);
    var eastMalaysiaVisible = eastMalaysiaBounds.intersects(bounds);

    if (map.getZoom() <= 7) {
        if (!showCountryStats) {
            showCountryStats = true
            showStateStats = false
            getCountryData((response) => {
                addEastWestMalaysiaMarker(map, response["east_malaysia_total_potholes"], response["west_malaysia_total_potholes"])
                removeAllAnnotateMarker()
                removeStateMalaysiaMarker()
            })
        }
        return;
    } else {
        if (map.getZoom() >= 8 && map.getZoom() <= 9) {
            if (!showStateStats) {
                showStateStats = true
                getStateData((response) => {
                    addStateMalaysiaMarker(map, response)
                    removeAllAnnotateMarker()
                    removeEastWestMalaysiaMarker()
                })
            }
            showCountryStats = false;
            return;
        } else {
            getAllData((response) => {
                if (annotateMarker.length == 0) {
                    response.forEach((obj) => {
                        if (obj.isAnnotated) {
                            if (obj.annotation.pothole > 0) {
                                marker = addMarker(map, obj.location.latlng.latitude, obj.location.latlng.longitude, obj)
                                annotateMarker.push({ "id": obj.id, "marker": marker })
                            }
                        }

                    })
                    removeEastWestMalaysiaMarker()
                    removeStateMalaysiaMarker()
                }
            })
            showCountryStats = false;
            showStateStats = false;
            return;
        }
    }
}

function limitEventsPerSecond(callback, limit) {
    var timerId;
    var counter = 0;

    function resetCounter() {
        counter = 0;
    }

    return function () {
        counter++;
        clearTimeout(timerId);

        if (counter === 1) {
            // First event, execute immediately
            callback.apply(this, arguments);
            timerId = setTimeout(resetCounter, 1000);
        } else if (counter <= limit) {
            // Events within the limit, execute after a delay
            timerId = setTimeout(function () {
                callback.apply(this, arguments);
                timerId = setTimeout(resetCounter, 1000);
            }, 1000 / limit);
        } else {
            // Exceeded the limit, do not execute the event
        }
    };
}

function addEastWestMalaysiaMarker(map, num_east, num_west) {
    var eastMalaysia = { lat: 4.2105, lng: 114.3310 };
    var westMalaysia = { lat: 3.7896, lng: 103.0644 };

    eastMalaysiaMarker = new google.maps.Marker({
        position: eastMalaysia,
        map: map,
        icon: getMarkerIcon(num_east, "white"), // Set the number of potholes for the marker
        label: { text: num_east.toString(), color: 'gray', fontFamily: 'Inter' }, // Display the number of potholes as a label
        zIndex: 1000
    });

    westMalaysiaMarker = new google.maps.Marker({
        position: westMalaysia,
        map: map,
        icon: getMarkerIcon(num_west, "white"), // Set the number of potholes for the marker
        label: { text: num_west.toString(), color: 'gray', fontFamily: 'Inter' }, // Display the number of potholes as a label
        zIndex: 1000
    });

}

function addStateMalaysiaMarker(map, data) {
    const stateCoordinates = {
        "Johor": { lat: 1.4853689, lng: 103.7618154 },
        "Kedah": { lat: 5.6977618, lng: 100.5372026 },
        "Kelantan": { lat: 6.1253977, lng: 102.2380715 },
        "Melaka": { lat: 2.189594, lng: 102.2500868 },
        "Negeri Sembilan": { lat: 2.7264243, lng: 101.9373483 },
        "Pahang": { lat: 3.622501, lng: 102.1175029 },
        "Perak": { lat: 4.5689623, lng: 101.094189 },
        "Perlis": { lat: 6.4413248, lng: 100.1983993 },
        "Pulau Pinang": { lat: 5.4163452, lng: 100.3327612 },
        "Sabah": { lat: 5.9788393, lng: 116.0753155 },
        "Sarawak": { lat: 2.559750, lng: 113.001089 },
        "Selangor": { lat: 3.37917, lng: 101.52933 },
        "Terengganu": { lat: 5.3116918, lng: 103.1322383 },
        "Wilayah Persekutuan Kuala Lumpur": { lat: 3.139003, lng: 101.686855 },
        "Labuan Federal Territory": { lat: 5.2802815, lng: 115.2473156 },
        "Putrajaya": { lat: 2.9264, lng: 101.6964 }
    };

    // Iterate over each key-value pair in the dictionary
    for (const state in stateCoordinates) {
        if (stateCoordinates.hasOwnProperty(state)) {
            if (data[state] > 0) {
                const coordinates = stateCoordinates[state];
                const lat = coordinates.lat;
                const lng = coordinates.lng;
                var temp = new google.maps.Marker({
                    position: coordinates,
                    map: map,
                    icon: getMarkerIcon(data[state], "gray"), // Set the number of potholes for the marker
                    label: { text: data[state].toString(), color: 'white', fontFamily: 'Inter' }, // Display the number of potholes as a label
                    zIndex: 1000
                });
                stateMalaysiaMarker.push(temp)
            }
        }
    }
}

function addMarker(map, latitude, longitude, data_obj) {
    var marker = new google.maps.Marker({
        position: new google.maps.LatLng(latitude, longitude),
        map: map,
        icon: getMarkerIcon(data_obj.annotation.pothole.toString(), data_obj.annotation.isAcknowledged ? "#575757" : "#f02b60", true),
        label: {
            text: data_obj.annotation.pothole.toString(),
            color: 'white',
            fontSize: '14px',
            fontFamily: 'Inter'
        }
    });
    // Open info window when marker is clicked
    marker.addListener('click', function () {
        openPanel(`${data_obj.id}`)
    });

    return marker
}

function removeStateMalaysiaMarker(map) {
    if (stateMalaysiaMarker.length > 0) {
        stateMalaysiaMarker.forEach(function (item) {
            item.setMap(null)
        })
    }
    stateMalaysiaMarker = []
}

function removeEastWestMalaysiaMarker(map) {
    if (eastMalaysiaMarker) {
        eastMalaysiaMarker.setMap(null)
    }
    if (westMalaysiaMarker) {
        westMalaysiaMarker.setMap(null)
    }
    eastMalaysiaMarker = null
    westMalaysiaMarker = null
}

function removeAllAnnotateMarker() {
    annotateMarker.forEach(function (marker_dict) {
        marker_dict["marker"].setMap(null)
    })
    annotateMarker = []
}

// Get Marker Icon
function getMarkerIcon(count, color, isAnnotated = false) {
    if (isAnnotated) {
        return {
            path: "M32 62c0-17.1 16.3-25.2 17.8-39.7A18 18 0 1 0 14 20a17.7 17.7 0 0 0 .2 2.2C15.7 36.8 32 44.9 32 62z",
            fillColor: color,
            fillOpacity: 0.8,
            strokeWeight: 0,
            scale: 0.7,
            anchor: new google.maps.Point(32, 60),
            labelOrigin: new google.maps.Point(32, 20)
        };
    } else {
        return {
            path: google.maps.SymbolPath.CIRCLE,
            fillColor: color,
            fillOpacity: 0.8,
            strokeWeight: 0,
            scale: (Math.sqrt(count) * 10) + 20 // Adjust the marker size based on the number of potholes
        };
    }
}

function getAllData(callback) {
    $.ajax({
        url: '/api/geo/all',
        type: 'GET',
        success: function (response) {
            callback(response)
        },
    });
}

function getCountryData(callback) {
    $.ajax({
        url: '/api/geo/country',
        type: 'GET',
        success: function (response) {
            callback(response)
        },
    });
}

function getStateData(callback) {
    $.ajax({
        url: '/api/geo/state',
        type: 'GET',
        success: function (response) {
            callback(response)
        },
    });
}