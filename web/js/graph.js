var smoothie,
  lines = {},
  colors = [ 'rgb(0, 200, 0)', 'rgb(150, 200, 255)', 'rgb(255, 100, 100)', 'rgb(180, 180, 180)' ],
  range = [ 19, 27 ];

$(function() {
  smoothie = new SmoothieChart({ minValue: range[0], maxValue: range[1], millisPerPixel: 40,
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
    success: function(data) {

      // the data comes from the server reverse-chronological
      data.tmp.reverse();
      data.idle.reverse();

      $.each(data.tmp, function(i, event) {
        var line = getLine(event.id);
        if ((line.ts || 0) > event.ts) return;
        line.ts = event.ts;
        line[0].append(event.ts, event.tmp);
        if ($.grep(data.idle, function(x) {
          return x.id === event.id && Math.abs(x.ts - event.ts) < 500 ;
        }).length)
          getLine(event.id)[1].append(event.ts, event.tmp);
      });
    },
    complete: function() {
      setTimeout(update, 1000);
    }
  });
}
