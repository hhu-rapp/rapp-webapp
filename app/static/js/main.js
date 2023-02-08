document.addEventListener('DOMContentLoaded', function() {
    var elems = document.querySelectorAll('.modal');
    var instances = M.Modal.init(elems);
});

document.addEventListener('DOMContentLoaded', function() {
    var elems = document.querySelectorAll('select');
    var instances = M.FormSelect.init(elems);
  });

$(document).ready(function () {
    $('#query-results').DataTable();
    $('#T_prediction').DataTable({
       "scrollX": true});
    var elems = document.querySelectorAll('select');
    var instances = M.FormSelect.init(elems, {});
});
