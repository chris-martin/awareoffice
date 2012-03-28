var smoothie,
  lines = {},
  colors = [ 'rgb(0, 200, 0)', 'rgb(150, 200, 255)', 'rgb(255, 100, 100)', 'rgb(180, 180, 180)' ],
  range = [ 19, 27 ];

$(function() {
  smoothie = new SmoothieChart({ minValue: range[0], maxValue: range[1],
    grid: { verticalSections: range[1]-range[0], millisPerLine: 1000 } });
  smoothie.streamTo($('canvas')[0]);
  update();
});

function getLine(id) {

  return lines[id] = lines[id] || createLine();

  function createLine() {
    var line = [ new TimeSeries(), new TimeSeries() ];
    var lineCount = $.map(lines, function() { return true; }).length;
    if (!lineCount) $('.legend').empty().text('Sensors:');
    var color = colors[lineCount % colors.length];
    smoothie.addTimeSeries(line[0], { strokeStyle: color, lineWidth: 2 });
    smoothie.addTimeSeries(line[1], { strokeStyle: color, lineWidth: 4, dots: true });
    $('<span class="sensor"/>').text(id).appendTo('.legend').css({ color: color, borderColor: color });

    return line;
  }

}

function update() {
  $.ajax({
    url: 'all.json',
    dataType: 'json',
    timeout: 1000,
    success: function(data) {
      $.each(data.temperature_events, function(i, event) {
        if (i != data.temperature_events.length - 1) return;
        getLine(event.sensor_id)[0].append(event.timestamp * 1000, event.temperature);
        if ($.grep(data.idle_events, function(x) {
          return x.sensor_id === event.sensor_id && Math.abs(x.timestamp - event.timestamp) < 0.5;
        }).length)
          getLine(event.sensor_id)[1].append(event.timestamp * 1000, event.temperature);
      });
    },
    complete: function() {
      setTimeout(update, 500);
    }
  });
}
