(function($) {

  var status = [
    {
      sensor: 'Chris Martin',
      status: 'available',
      idleTime: 181394
    },
    {
      sensor: 'Kelsey Francis',
      status: 'away',
      idleTime: 903294
    }
  ];

  function update() {
    render();
    $.ajax({
      url: 'status.json',
      dataType: 'json',
      success: function(data) {
        status = data;
        render();
      },
      complete: function() {
        setTimeout(update, 1000);
      }
    });
  }

  function render() {
    $('.sensor-status').empty();
    $.each(status, function(key, s) {
      $('<li/>').
        append($('<img/>', { 'class': 'status-icon', src: statusIconUrl(s.status) })).
        append($('<span/>', { 'class': 'sensor-name', text: sensorName(s.sensor) })).
        append($('<span/>', { 'class': 'idle-time', text: formatTime(s.idleTime) })).
        appendTo($('ul.sensor-status'));
    });
  }

  function sensorName(sensor) {
    return sensor;
  }

  function statusIconUrl(status) {
    return 'img/status-icons/' + status + '.svg';
  }

  function formatTime(ms) {
    var m = Math.round(ms / 1000 / 60);
    var h = Math.floor(m / 60);
    return h + ':' + (m < 10 ? '0' + m : m);
  }

  $(function() {
    update();
  });
})(jQuery);
