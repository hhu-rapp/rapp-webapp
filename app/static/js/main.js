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


// Group-level Prediction
$(function () {
    $('.feature-link').click(function (event) {
        event.preventDefault(); // prevent the link from following the href

        const selectedFeature = $(this).text();

        // Update the feature button text
        var featureSelect = document.getElementById('featureSelectButton');
        featureSelect.innerHTML = selectedFeature;
        // Get the current aggregation
        var aggSelect = document.getElementById('aggregationSelectButton');
        var currentAgg = aggSelect.textContent;

        // Get the data
        $.getJSON(/group_level_prediction/ + $SCRIPT_PARAMS, {
            feature: selectedFeature,
            aggregation: currentAgg,
        }, function (data) {
            $('#T_group_prediction').DataTable().destroy();
            $('#group-pred-table').html(data.styled_df);
            $('#T_group_prediction').DataTable({
                "scrollX": true
            });

        });

        return false;
    });

    $('.aggregation-link').click(function (event) {
        event.preventDefault(); // prevent the link from following the href

        const selectedAgg = $(this).text();
        // Update the aggregation button text
        var aggSelect = document.getElementById('aggregationSelectButton');
        aggSelect.innerHTML = selectedAgg;
        // Get the current feature
        var featureSelect = document.getElementById('featureSelectButton');
        var currentFeature = featureSelect.textContent;
        // Get the data
        $.getJSON(/group_level_prediction/ + $SCRIPT_PARAMS, {
            feature: currentFeature,
            aggregation: selectedAgg,
        }, function (data) {
            $('#T_group_prediction').DataTable().destroy();
            $('#group-pred-table').html(data.styled_df);
            $('#T_group_prediction').DataTable({
                "scrollX": true
            });

        });

        return false;
    });
});

//Performance History
// Performance Tabs
$('#performance-tabs a').on('click', function (e) {
    e.preventDefault()
    $(this).tab('show')
})

$('#performance-tabs a[data-toggle="tab"]').on('show.bs.tab', function (e) {
    let target = $(e.target).data('target');
    $('.tab-pane').not(target).removeClass('active show');
    $(target)
        .addClass('active show')
});
