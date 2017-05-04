function updateTable(content) {
    // TODO: Merge this part before ajax across all update functions

    var paramSet = {};
    var hasAny = false;
    //var labels = [];

    content.find(".row.param").each(function () {
        var params = {};
        //var label = "";
        $(this).find("select.form-control").each(function () {
            var value = $(this).val()
            params[$(this).attr("id")] = value;
            //label += label === "" ? value : (" " + value);
            if(hasAny === false && $(this).val() !== ""){
                hasAny = true;
            }
        });
        //labels.push(label);
        paramSet[$(this).attr("id")] = params;
    });
    var requestJSON = {"chartId" : content.parent().attr("id"), "requestParams" : paramSet};
    //var chart = content.find(".ct-chart.line");
    var tbody = content.find("tbody");
    //var tbody = table.children('tbody');
    //console.log(labels);
    if(hasAny){
        $.ajax({
            type: "POST",
            url: "/getChartData",
            contentType:"application/json",
            data : JSON.stringify(requestJSON),
            success: function(resultJSON) {
                if($.trim(resultJSON)) {
                    // If response isn't empty
                    var result = JSON.parse(resultJSON);

                    if (!$.isEmptyObject(result)) {
                        tbody.html("");
                        for(var course in result){
                            console.log(typeof result[course]);
                            tbody.append("<tr><td>"+course+"</td><td>"+(result[course]*100).toFixed(1)+"%</td></tr>>")
                        }
                    }
                    else {
                        tbody.html("<p style='text-align:center; vertical-align:middle'>No data found for given parameters.</p>");
                    }
                }
                else {
                    tbody.html("<p style='text-align:center; vertical-align:middle'>Query submission error.</p>");
                }
            },
            error: function() {
                alert('error');
            }
        });
    }
    else{
        tbody.html("");
    }
}

// Updates a line chart based on the currently selected filters
function updateChart(content) {
    var paramSet = {};
    var hasAny = false;
    var labels = [];
    content.find(".row.param").each(function () {
        var params = {};
        var label = "";
        $(this).find("select.form-control").each(function () {
            var value = $(this).val()
            params[$(this).attr("id")] = value;
            label += label === "" ? value : (" " + value);
            if(hasAny === false && $(this).val() !== ""){
                hasAny = true;
            }
        });
        labels.push(label);
        paramSet[$(this).attr("id")] = params;
    });
    var requestJSON = {"chartId" : content.parent().attr("id"), "requestParams" : paramSet};
    var chart = content.find(".ct-chart.line");
    console.log(labels);
    if(hasAny){
        $.ajax({
            type: "POST",
            url: "/getChartData",
            contentType:"application/json",
            data : JSON.stringify(requestJSON),
            success: function(resultJSON) {
                if($.trim(resultJSON)) {
                    var result = JSON.parse(resultJSON);
                    var data = {
                        labels: result['labels'],
                        series: result['series']
                    };
                    var options = {
                        lineSmooth: Chartist.Interpolation.none({
                            fillHoles: true
                        }),
                        plugins: [
                                Chartist.plugins.legend({
                                    legendNames: labels
                                }),
                                Chartist.plugins.tooltip()
                            ]
                    };
                    if (result['labels'].length !== 0) {
                        chart.html("");
                        new Chartist.Line('#' + chart.attr("id"),data, options);
                    }
                    else {
                        chart.html("<p style='text-align:center; vertical-align:middle'>No data found for given parameters.</p>");
                    }
                }
                else {
                    chart.html("<p style='text-align:center; vertical-align:middle'>Query submission error.</p>");
                }
            },
            error: function() {
                alert('error');
            }
        });
    }
    else{
        chart.html("");
    }
}

function updateView(viewType, content){
    switch(viewType){
        case "line-chart-view":
            updateChart(content);
            break;
        case "table-view":
            updateTable(content);
            break;
        default:
            //
    }
}

// Populates a saved query dropdown for the given object
function populateSavedQuery(dataStore, controls, _callback) {
    var parent_id = controls.parent().attr("id");
    $.ajax({
        type: "POST",
        url: "/savedQueries",
        contentType: "application/json",
        data: JSON.stringify({'view_id': controls.parent().attr("id")}),
        success: function(resultJSON) {
            dataStore[parent_id] = resultJSON;
            var savedQueries = JSON.parse(resultJSON);
            var queryName = controls.find("select[name='queryName']");
            queryName.find('option').remove();
            queryName.append($('<option>', {
                    value: "",
                    text: ""
                }));
            var key;
            for (key in savedQueries) {
                queryName.append($('<option>', {
                    value: key,
                    text: savedQueries[key].name
                }));
            }
            typeof _callback === 'function' && _callback(key);
        },
        error: function(){
            alert("error");
        }
    });
}

$(document).ready(function(){

    // Initializes line charts
    $(".ct-chart.line").each(function () {

        var data = {
                        labels: [],
                        series:[[]]
                    };
        var options = {
                        lineSmooth: Chartist.Interpolation.none({
                            fillHoles: true
                        }),
                        plugins: [
                                Chartist.plugins.legend({
                                    legendNames: []
                                }),
                                Chartist.plugins.tooltip()
                            ]

                    };
        new Chartist.Line('#' + $(this).attr("id"), data, options);
    });
    // Populates the saved queries for all cards
    var dataStore = {};
    $('.query-controls').each(function () {
        populateSavedQuery(dataStore, $(this));
    });
    // Updates charts whenever a filter is changed
    var forms = $(".card form");
    forms.on('change',  'select.combobox', function () {
        $(this).closest(".card").find("select[name='queryName']").val("");
        console.log($(this).closest(".card").find("select[name='queryName']"));
        updateView($(this).closest(".card").attr("type"), $(this).closest(".content"));
    });
    // Updates filters and chart whenever the selected saved query is changed
    $(".query-controls select[name='queryName']").change(function(){
        // TODO: Remove dependence on ".row .add"
        var select = $(this);
        if (select.val()) {
            var card = select.closest("div.card");
            var firstRow = card.find('.row.param').first();
            firstRow.attr("id", "row0");
            card.find('.row.param').remove();
            var queryData = JSON.parse(JSON.parse(dataStore[card.attr("id")])[select.val().toString()]['query_data']);
            var content = card.find('.content').eq(0);
            for(var row in queryData){
                var rowData = queryData[row];
                var lastRow = content.find('.row.param').last();
                var newRow;
                if (lastRow.length === 0){
                    newRow =  firstRow.clone();
                }
                else{
                    newRow = lastRow.clone()
                    var rowId = parseInt(newRow.attr("id").slice(3)) + 1;
                newRow.attr("id", "row" + rowId);
                }
                for (var key in rowData) {
                    newRow.find("select#" + key).val(rowData[key]);
                }
                newRow.insertBefore(content.find(".row.add"));
            }
            updateView(card.attr("type"), content);
        }
    });
    // Deletes a row of filters (a new series) for charts
    forms.on('click', 'div.row button.clear', function () {
        var row = $(this).closest('.row');
        var form = row.closest('form');
        if(form.children('.row').length > 2){
            row.remove();
        }
        else {
            $(this).closest('.row').find(".form-group select").each(function () {
                $(this).val("");
            });
        }
        updateView(form.closest(".card").attr("type"), form.closest('.content'));
    });
    // Adds a new row of filters (series)
    $(".card form button.add").click(function () {
        var prevRow = $(this).closest('.row').prev();
        var newRow = prevRow.clone();
        var rowId = parseInt(newRow.attr("id").slice(3)) + 1;
        newRow.attr("id", "row" + rowId);
        newRow.insertAfter(prevRow);
    });
    // Modal to save query data. Gathers all data into the form.
    var saveModal = $('#saveQuery');
    saveModal.on('show.bs.modal', function (e) {
      var card = $(e.relatedTarget).closest(".card");
      var data = {};
      var visualizationId = card.attr("id");
      var content = card.find(".content");
      var rowId = 0;
      content.find(".row.param").each(function () {
          var row = {};
          $(this).find("select.form-control").each(function () {
              row[$(this).attr("id")] = $(this).val();
          });
          data["row"+ rowId++] = row;//$.extend( {}, row );
      });
      $(this).find("input[name='_queryData']").val(JSON.stringify(data));
      $(this).find("input[name='_visualizationId']").val(visualizationId);
    });
    // Saves query data
    saveModal.find('button.btn-primary').on('click', function () {
       var modal = $(this).closest("#saveQuery");
       var visualizationId = modal.find("input[name='_visualizationId']").val();
       var queryName =  modal.find("input#name").val();
       console.log("oi");
        $.ajax({
            type: "POST",
            url: "/saveQuery",
            contentType: "application/json",
            data: JSON.stringify({'view_id': visualizationId, "query_name" : queryName, "query_data" : modal.find("input[name='_queryData']").val() }),
            success: function() {
                targetControls = $("html").find("#" + modal.find("input[name='_visualizationId']").val() + " .query-controls");
                populateSavedQuery(dataStore, targetControls, function (id) {
                    targetControls.find("select[name='queryName']").eq(0).val(id);
                });
                // Set the value of the dropdown to the value just created
                //TODO: make this work (problem is with the async ajax call)
                //targetControls.find("select[name='queryName']").eq(0).val(queryName);
            },
            error: function(){
                //
            }
       });
    });

});




