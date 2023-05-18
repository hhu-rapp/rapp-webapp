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

// Ajax Individual Performance
$(document).ready(function() {
     var loadingDiv = $('.perfLoading');
    $.ajax({
      url: "/individual_performance/2000000", 
     method: "GET", 
    beforeSend: function() {
      // Remove the "fade" class to show the loading <div>
      loadingDiv.removeClass('fade');
    },
    success: function(data) {
      // Parse the data received from the backend
      var jsonData = JSON.parse(data);

      // Extract the necessary columns from the data
      var numSemesterData = jsonData.map(function(item) {
        return item.Num_Semester;
      });
      var ectsData = jsonData.map(function(item) {
        return item.ECTS;
      });

      // Create the chart using Charts.js
      var ctx = document.getElementById('individual-perf-chart').getContext('2d');
      var chart = new Chart(ctx, {
        type: 'line',
        data: {
          labels: numSemesterData,
          datasets: [{
            label: 'ECTS',
            data: ectsData,
            borderColor: '#006ab3',
            backgroundColor: '#006ab3',
            borderWidth: 3,
          }]
        },
        options: {
          responsive: true,
          scales: {
            y: {
              beginAtZero: true,
             title: {
                    display: true,
                    text: 'Cumulative ECTS'
                }
            },
            x: {
                title: {
                    display: true,
                    text: 'Semester'
                }
            }
          }
        }
      });
      loadingDiv.addClass('fade');
    },
    error: function() {
      console.error("Failed to fetch data from the backend.");
      loadingDiv.addClass('fade');
    }
  });
});
