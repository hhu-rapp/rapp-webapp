document.addEventListener('DOMContentLoaded', function() {
    var elems = document.querySelectorAll('.sidenav');
    var options = {'outDuration': 0}
    var instances = M.Sidenav.init(elems, options);
});

document.addEventListener('DOMContentLoaded', function() {
    var elems = document.querySelectorAll('.tabs');
    var instance = M.Tabs.init(elems);
});

$(document).ready(function () {
    $('#query-results').DataTable();
    var elems = document.querySelectorAll('select');
    var instances = M.FormSelect.init(elems, {});
});