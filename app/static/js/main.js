$(document).ready(function () {
    // $('#query-results').DataTable();

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
