var bounds = new google.maps.LatLngBounds();
var polylineBeforeState = true;
var powerlineMarkers = [];
var map = new google.maps.Map(document.getElementById("map_canvas"), {
    zoom: 15,
});

function makeButton(text, listener) {
    var button = document.createElement('button');
    button.classList.add('map-option');
    button.innerText = text;
    map.controls[google.maps.ControlPosition.TOP_CENTER].push(button);
    button.addEventListener('click', listener);
}

unassigned.forEach(client => {
    bounds.extend(new google.maps.LatLng(client.lat, client.lng));

    var marker = new google.maps.Marker({
        position: {lat: client.lat, lng: client.lng},
        map,
        icon: house_img_url,
    });

    var infowindow = new google.maps.InfoWindow({
        content: 'Unassigned client',
    });

    marker.addListener('click', () => {
        infowindow.open(map, marker);
    });
});

facilities.forEach(facility => {
    bounds.extend(new google.maps.LatLng(facility.lat, facility.lng));

    facility.marker = new google.maps.Marker({
        position: {lat: facility.lat, lng: facility.lng},
        map,
        icon: fac_img_url,
        visible: facility.assignedClients.length !== 0,
    });

    var clientMarkers = facility.assignedClients.map(client => {
        bounds.extend(new google.maps.LatLng(client.lat, client.lng));

        return new google.maps.Marker({
            position: {lat: client.lat, lng: client.lng},
            visible: false,
            map,
            icon: house_small_url,
        });
    });

    if(facility.assignedClients.length === 0) {
        var content = 'Unused facility';
    } else if(facility.assignedClients.length === 1) {
        var content = '<p>1 client</p>';
    } else {
        var content = `<p>${facility.assignedClients.length} clients</p>`;
    }

    var infowindow = new google.maps.InfoWindow({content});

    facility.marker.addListener('click', () => {
        infowindow.open(map, facility.marker);
        if(clientMarkers.length === 0) return;
        var new_visible = !clientMarkers[0].getVisible();
        for(client of clientMarkers) {
            client.setVisible(new_visible);
        }
    });
});

for(line of powerlines) {
    bounds.extend(line.start);
    bounds.extend(line.end);

    line.polyline = new google.maps.Polyline({
        path: [line.start, line.end],
        strokeColor: line.beforeColor,
        strokeOpacity: 1.0,
        strokeWeight: 5,
        visible: false,
        map,
    });

    powerlineMarkers.push(line.polyline);

    if(line.type.toLowerCase() === 'substation') {
        var marker = new google.maps.Marker({
            position: line.start,
            map,
            visible: false,
        });

        powerlineMarkers.push(marker);
    }
}

makeButton('Toggle line visibility', () => {
    powerlineMarkers.forEach(icon => icon.setVisible(!icon.getVisible()));
});

makeButton('Toggle grid improvements', () => {
    for(line of powerlines) {
        var newColor = polylineBeforeState ? line.afterColor : line.beforeColor;
        line.polyline.setOptions({strokeColor: newColor});
    }
    polylineBeforeState = !polylineBeforeState;
});

makeButton('Toggle unused facility visibility', () => {
    facilities.filter(facility => facility.assignedClients.length === 0)
              .forEach(facility => {
                   facility.marker.setVisible(!facility.marker.getVisible());
               });
});

map.fitBounds(bounds);
map.panToBounds(bounds);
