$(document).ready(function () {
    // $('#query-results').DataTable();
    $('#T_prediction').DataTable({
        "scrollX": true
    });
    var modals = document.querySelectorAll('.modal');
    var modalOptions = {
        backdrop: true,
        keyboard: true,
        focus: true
    };

    modals.forEach(function (modal) {
        var myModal = new bootstrap.Modal(modal, modalOptions);
    });
});

document.addEventListener("DOMContentLoaded", function () {
    document.querySelector(".dash-content").classList.add("show");
});


//Prediction

// Prediction Tabs
$('#prediction-tabs a').on('click', function (e) {
    e.preventDefault()
    $(this).tab('show')
})

$('#prediction-tabs a[data-toggle="tab"]').on('show.bs.tab', function (e) {
    let target = $(e.target).data('target');
    $('.tab-pane').not(target).removeClass('active show');
    $(target)
        .addClass('active show')
});
