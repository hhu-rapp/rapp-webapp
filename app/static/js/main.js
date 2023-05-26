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
var chart = null;
var groupChart = null;

function fetchIndividualPerformance(studentId) {
    const url = "/individual_performance/" + studentId;
    const loadingDiv = $('.perfLoading');
    $.ajax({
        url: url,
        method: "GET",
        beforeSend: function () {
            // Remove the "fade" class to show the loading <div>
            loadingDiv.removeClass('fade');
    },
    success: function(data) {
      // Parse the data received from the backend
      const jsonData = JSON.parse(data);

      // Extract the necessary columns from the data
      const numSemesterData = jsonData.data.map(function(item) {
        return item.Num_Semester;
      });
      const ectsData = jsonData.data.map(function(item) {
        return item.ECTS;
      });
      const studentMajor = jsonData.major;
      const studentDegree = jsonData.degree;
      
      
      // Check if the chart instance already exists
      if (chart) {
        // Update the chart's data
        chart.data.labels = numSemesterData;
        chart.data.datasets[0].data = ectsData;
        chart.options.plugins.title.text = 'Matrikelnummer: ' + studentId;
        chart.options.plugins.subtitle.text = studentMajor + ' (' + studentDegree + ')';

        // Redraw the chart
        chart.update();
      } else {

          // Create the chart using Charts.js
          const ctx = document.getElementById('individual-perf-chart').getContext('2d');

          chart = new Chart(ctx, {
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
                  },
                    plugins: {
                        title: {
                            display: true,
                            text: 'Matrikelnummer: ' + studentId
                        },
                        subtitle: {
                            display: true,
                            text: studentMajor + ' (' + studentDegree + ')'
                        },
                    
                    }
                  
              }
          });
      }
      loadingDiv.addClass('fade');
    },
    error: function() {
      console.error("Failed to fetch data from the backend.");
      loadingDiv.addClass('fade');
    }
  });
}

$(document).ready(function() {
  const studentId = 0;
    fetchIndividualPerformance(studentId);

    $('#perf-studentId-btn').click(function () {

        const studentId = $('#perf-studentId-input').val();
        
        fetchIndividualPerformance(Number(studentId));
    });
});

// Ajax Group Performance

function fetchGroupPerformance(groupId) {

    const url = "/group_performance/" + groupId;
    const loadingDiv = $('.perfLoading');

    $.ajax({
        url: url,
        method: "GET",
        beforeSend: function () {
            // Remove the "fade" class to show the loading <div>
            loadingDiv.removeClass('fade');
        },
        success: function (data) {
            // Parse the data received from the backend
            const jsonData = JSON.parse(data);

            var masterData = jsonData.filter(function (item) {
                return item.Degree === 'Master';
            });

            // Extract the necessary columns for Master degree
            var masterNumSemesterData = masterData.map(function (item) {
                return item.Num_Semester;
            });
            var masterEctsData = masterData.map(function (item) {
                return item.ECTS;
            });
            
            // Filter the data for Bachelor degree
            const bachelorData = jsonData.filter(function (item) {
                return item.Degree === 'Bachelor';
            });

            // Extract the necessary columns for Bachelor degree
            const bachelorNumSemesterData = bachelorData.map(function (item) {
                return item.Num_Semester;
            });
            const bachelorEctsData = bachelorData.map(function (item) {
                return item.ECTS;
            });

            // Check if the chart instance already exists
            if (groupChart) {
                // Update the chart's data
                groupChart.data.labels = bachelorNumSemesterData;
                groupChart.data.datasets[0].data = masterEctsData;
                groupChart.data.datasets[1].data = bachelorEctsData;

                // Redraw the chart
                groupChart.update();
            } else {

                // Create the chart using Charts.js
                const ctx = document.getElementById('group-perf-chart').getContext('2d');
                groupChart = new Chart(ctx, {
                    type: 'line',
                    data: {
                        labels: bachelorNumSemesterData,
                        datasets: [{
                            label: 'Master',
                            data: masterEctsData,
                            borderColor: '#006ab3',
                            backgroundColor: '#006ab3',
                            borderWidth: 3,
                        }, {
                            label: 'Bachelor',
                            data: bachelorEctsData,
                            borderColor: '#ff7f50',
                            backgroundColor: '#ff7f50',
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
                                    text: 'AVG. ECTS'
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
            }

            loadingDiv.addClass('fade');
        },
        error: function () {
            console.error("Failed to fetch data from the backend.");
            loadingDiv.addClass('fade');
        }
    });
}


$(document).ready(function () {
        const groupId = 'degree';
        fetchGroupPerformance(groupId);

        //  $('#perf-groupId-btn').click(function() {
        //     
        //     const groupId = $('#perf-groupId-input').val();
        //
        //     fetchGroupPerformance(groupId);
        // });
    }
);

//Risk Analysis
//Ajax Risk Analysis

var riskChart = null;


function fetchRiskAnalysis(featureId) {

    const url = "/get_risk_analysis/" + featureId;
    const loadingDiv = $('.riskLoading');

    $.ajax({
        url: url,
        method: "GET",
        beforeSend: function () {
            // Remove the "fade" class to show the loading <div>
            loadingDiv.removeClass('fade');
        },
        success: function (data) {
            // Parse the data received from the backend
            const jsonData = JSON.parse(data);
            
            const dataLabels = jsonData.labels;
            const graduateData = jsonData.graduate;
            const dropoutData = jsonData.dropout;
            
            // Check if the chart instance already exists
            if (riskChart) {
                // Update the chart's data
                riskChart.data.labels = dataLabels;
                riskChart.data.datasets[0].data = graduateData;
                riskChart.data.datasets[1].data = dropoutData;

                // Redraw the chart
                riskChart.update();
            } else {

                // Create the chart using Charts.js
                const ctx = document.getElementById('risk-chart').getContext('2d');
                riskChart = new Chart(ctx, {
                    type: 'bar',
                    data: {
                        labels: dataLabels,
                        datasets: [{
                            label: 'Graduate',
                            data: graduateData,
                            borderColor: '#015f9f',
                            backgroundColor: '#006ab3',
                            borderWidth: 1,
                        }, {
                            label: 'Dropout',
                            data: dropoutData,
                            borderColor: '#ea4a4a',
                            backgroundColor: '#ff5050',
                            borderWidth: 1,
                        }]
                    },
                    options: {
                        responsive: true,
                        scales: {
                            y: {
                                stacked: true,
                            },
                            x: {
                                stacked: true,
                            },},
                            plugins: {
                                title: {
                                    display: true,
                                    text: 'Dropout Analysis'
                                },
                            }
                        
                    }
                });
            }

            loadingDiv.addClass('fade');
        },
        error: function () {
            console.error("Failed to fetch data from the backend.");
            loadingDiv.addClass('fade');
        }
    });
    
}

$(document).ready(function () {
    const featureId = 'Sex';
    fetchRiskAnalysis(featureId);

    $('input[name="riskFeatureRadioOption"]').change(function () {
        const featureId = $(this).val();
        fetchRiskAnalysis(featureId);
    });
});
