// Wait for the DOM to load
document.addEventListener('DOMContentLoaded', function () {
    const mapDiv = document.getElementById('choropleth-map');

    // Add hover interaction to change opacity
    mapDiv.on('plotly_hover', function (data) {
        const location = data.points[0].location;
        const newOpacity = data.points.map(point => point.location === location ? 1.0 : 0.3);
        Plotly.restyle('choropleth-map', 'marker.opacity', [newOpacity]);
    });

    mapDiv.on('plotly_unhover', function () {
        const defaultOpacity = Array.from(mapDiv.data[0].locations).fill(0.7);
        Plotly.restyle('choropleth-map', 'marker.opacity', [defaultOpacity]);
    });
});
