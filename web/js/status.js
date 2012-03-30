(function($) {

  var statuses = [];

  function update() {
    $.ajax({
      url: 'status.json',
      dataType: 'json',
      success: function(data) {
        var ids = $.map(data, function(x, id) { return id; });
        ids.sort();
        statuses = $.map(ids, function(id) { return $.extend({id: id}, data[id]); });
        render();
      },
      complete: function() {
        setTimeout(update, 1000);
      }
    });
  }

  function render() {
    $('.sensor-status').empty();
    $.each(statuses, function(key, s) {
      $('<li/>').
        append($('<img/>', { 'class': 'status-icon', src: statusIconUrl(s.status) })).
        append($('<span/>', { 'class': 'sensor-name', text: sensorName(s.id) })).
        append($('<span/>', { 'class': 'idle-time', text: s.status === 'available' ? '' : formatTime(s.idle_time) })).
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
    if (!ms) return '';

    var s = Math.floor(ms / 1000) % 60;
    var m = Math.floor(ms / (1000*60)) % 60;
    var h = Math.floor(ms / (1000*60*60));

    return h + ':' + zeropad(m) + ':' + zeropad(s);
    function zeropad(x) { return x < 10 ? '0' + x : x; }
  }

  $(function() {
    update();
  });
})(jQuery);
