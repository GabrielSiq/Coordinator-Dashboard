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


function updateBar(content) {
    var paramSet = {};
    var hasAny = false;
    var labels = [];
    content.find(".row.param").each(function () {
        var label = "";
        var params = {};
        $(this).find("select.form-control").each(function () {
            var value = $(this).val();
            params[$(this).attr("id")] = value;
            label += label === "" ? value : (" " + value);
            if(hasAny === false && value !== ""){
                hasAny = true;
            }
        });
        paramSet[$(this).attr("id")] = params;
        labels.push(label);
    });
    var requestJSON = {"chartId" : content.closest('.card').attr("id"), "requestParams" : paramSet};
    var chart = content.find(".ct-chart.bar");
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
                        plugins: [
                            Chartist.plugins.legend({
                                legendNames: labels
                            }),
                            Chartist.plugins.tooltip()
                        ]
                    };
                    if (result['labels'].length !== 0) {
                        chart.html("");
                        new Chartist.Bar('#' + chart.attr("id"),data, options);
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

// Updates a line chart based on the currently selected filters
function updateChart(content) {
    var paramSet = {};
    var hasAny = false;
    var labels = [];
    content.find(".row.param").each(function () {
        var params = {};
        var label = "";
        $(this).find("select.form-control").each(function () {
            var value = $(this).val();
            params[$(this).attr("id")] = value;
            label += label === "" ? value : (" " + value);
            if(hasAny === false && $(this).val() !== ""){
                hasAny = true;
            }
        });
        labels.push(label);
        paramSet[$(this).attr("id")] = params;
    });
    var requestJSON = {"chartId" : content.closest('.card').attr("id"), "requestParams" : paramSet};
    var chart = content.find(".ct-chart.line");
    if(hasAny){
        $.ajax({
            type: "POST",
            url: "/getChartData",
            contentType:"application/json",
            data : JSON.stringify(requestJSON),
            success: function(resultJSON) {
                if($.trim(resultJSON)) {
                    var result = JSON.parse(resultJSON);
                    for(var i in result['labels']){
                        var labelString = result['labels'][i].toString();
                        var len = labelString.length;
                        result['labels'][i] = labelString.slice(len-3, len-1)+"."+labelString.slice(len-1, len)
                    }
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

function updatePie(content) {
    var paramSet = {};
    var hasAny = false;
    content.find(".row.param").each(function () {
        var params = {};
        $(this).find("select.form-control").each(function () {
            var value = $(this).val();
            params[$(this).attr("id")] = value;
            if(hasAny === false && value !== ""){
                hasAny = true;
            }
        });
        paramSet[$(this).attr("id")] = params;
    });
    var requestJSON = {"chartId" : content.closest('.card').attr("id"), "requestParams" : paramSet};
    var chart = content.find(".ct-chart.pie");
    if(hasAny){
        $.ajax({
            type: "POST",
            url: "/getChartData",
            contentType:"application/json",
            data : JSON.stringify(requestJSON),
            success: function(resultJSON) {
                if($.trim(resultJSON)) {
                    var result = JSON.parse(resultJSON);
                    var total = 0;
                    for(var i =0; i < result['labels'].length; i++){
                        total += result['series'][i]
                    }
                    var labels = [];
                    for(var i =0; i < result['labels'].length; i++){
                        labels[i] = (Math.round(result['series'][i]*10000/total)/100).toString() + '%';
                    }
                    var data = {
                        labels: labels,
                        series: result['series']
                    };
                    var options = {
                        plugins: [
                            Chartist.plugins.legend({
                                legendNames: result['labels']
                            }),
                            Chartist.plugins.tooltip()
                        ]
                    };
                    if (result['labels'].length !== 0) {
                        chart.html("");
                        new Chartist.Pie('#' + chart.attr("id"),data, options);
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
        case "bar-chart-view":
            updateBar(content);
            break;
        case "pie-chart-view":
            updatePie(content);
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
            typeof _callback === 'function' && _callback();
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
        updateView($(this).closest(".card").attr("type"), $(this).closest(".content"));
    });

    // Updates filters and chart whenever the selected saved query is changed
    $(".query-controls select[name='queryName']").change(function(){
        // TODO: Remove dependence on ".row .add"
        var select = $(this);
        var card = select.closest("div.card");
        if (select.val()) {
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
                    newRow = lastRow.clone();
                    var rowId = parseInt(newRow.attr("id").slice(3)) + 1;
                    newRow.attr("id", "row" + rowId);
                }
                for (var key in rowData) {
                    select = newRow.find("select#" + key);
                    if(select.attr("dynamic-endpoint") !== undefined){
                        field = select.attr("dynamic-field");
                        value = newRow.find("select#" + field).val();
                        $.ajax({
                            type: "POST",
                            url: select.attr("dynamic-endpoint"),
                            contentType: "application/json",
                            select : select,
                            key : key,
                            data: JSON.stringify({[field]: value}),
                            success: function(response) {
                                if($.trim(response)) {
                                    var optionsList = JSON.parse(response);
                                    this.select.find('option').remove();
                                    this.select.append($('<option>', {
                                        value: "",
                                        text: ""
                                    }));
                                    for (var i in optionsList) {
                                        this.select.append($('<option>', {
                                            value: optionsList[i],
                                            text: optionsList[i]
                                        }));
                                    }
                                }
                                this.select.val(rowData[this.key]);
                            },
                            error: function(){
                                //
                            }
                        });
                    }
                    else{
                        select.val(rowData[key]);
                    }
                }
                newRow.insertBefore(content.find(".row.add"));
            }
            updateView(card.attr("type"), content);
            card.find(".query-controls .delete-query").css('visibility','visible');
            card.find(".query-controls .rename-query").css('visibility','visible');
        }
        else{
            card.find(".query-controls .delete-query").css('visibility','hidden');
            card.find(".query-controls .rename-query").css('visibility','hidden');
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
        form.closest(".card").find("select[name='queryName']").val("");
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
        $.ajax({
            type: "POST",
            url: "/saveQuery",
            contentType: "application/json",
            data: JSON.stringify({'view_id': visualizationId, "query_name" : queryName, "query_data" : modal.find("input[name='_queryData']").val() }),
            success: function(response) {
                if($.trim(response)) {
                    targetControls = $("html").find("#" + visualizationId + " .query-controls");
                    populateSavedQuery(dataStore, targetControls, function () {
                        targetControls.find("select[name='queryName']").eq(0).val(response);
                    });
                }
                else{
                    window.location.reload();
                }
            },
            error: function(){
                console.log("Ajax error");
            }
        });
    });

    // Cosmetic changes for tables
    $("#sort").change(function () {
        var card = $(this).closest(".card");
        var sort = card.find(".category span");
        var arrow =  card.find(".title span");
        sort.text($(this).val());
        if($(this).val() === "largest"){
            sort.css('color', 'red');
            arrow.addClass('glyphicon-triangle-bottom');
        }
        else{
            sort.css('color', 'green');
            arrow.addClass('glyphicon-triangle-top');
        }

    });

    // Deleting saved queries
    $("button.delete-query").on('click', function () {
        card = $(this).closest(".card");
        $.ajax({
            type: "POST",
            url: "/deleteQuery",
            contentType: "application/json",
            data: JSON.stringify({'query_id': card.find("select[name='queryName']").val()}),
            success: function(response) {
                if($.trim(response)) {
                    populateSavedQuery(dataStore, card.find(".query-controls"));
                }
                else{
                    window.location.reload();
                }
            },
            error: function(){
                //
            }
        });
    });

    // Modal to rename query
    var renameModal = $("#renameQuery");
    renameModal.on('show.bs.modal', function (e) {
        var card = $(e.relatedTarget).closest(".card");
        var visualizationId = card.attr("id");
        var queryId = card.find("select[name='queryName']").val();
        var queryName = card.find("select[name='queryName'] option:selected").text();
        $(this).find("input[name='_queryId']").val(queryId);
        $(this).find("input[name='_visualizationId']").val(visualizationId);
        $(this).find("#name").val(queryName);
    });

    // Renames query
    renameModal.find('button.btn-primary').on('click', function () {
        var modal = $(this).closest("#renameQuery");
        var queryId = modal.find("input[name='_queryId']").val();
        var queryName =  modal.find("input#name").val();
        var visualizationId = modal.find("input[name='_visualizationId']").val();
        $.ajax({
            type: "POST",
            url: "/renameQuery",
            contentType: "application/json",
            data: JSON.stringify({'query_id': queryId, "query_name" : queryName}
            ),
            success: function(resultJSON) {
                if($.trim(resultJSON)){
                    targetControls = $("html").find("#" + visualizationId + " .query-controls");
                    populateSavedQuery(dataStore, targetControls, function () {
                        targetControls.find("select[name='queryName']").eq(0).val(queryId);
                    });
                }
                else{
                    window.location.reload();
                }
            },
            error: function(){
                console.log("Ajax error");
            }
        });
    });

    $("#avg-grade #course").on('change', function () {
        var course = $(this);
        $.ajax({
            type: "POST",
            url: "/getProfessors",
            contentType: "application/json",
            data: JSON.stringify({'course': $(this).val()}),
            success: function(response) {
                if($.trim(response)) {
                    profList = JSON.parse(response);
                    var professor = course.closest('.param').find('#professor');
                    professor.find('option').remove();
                    professor.append($('<option>', {
                        value: "",
                        text: ""
                    }));
                    for (var i in profList) {

                        professor.append($('<option>', {
                            value: profList[i],
                            text: profList[i]
                        }));
                    }

                }
            },
            error: function(){
                //
            }
        });
    });

    $.ajax({
            type: "POST",
            url: "/getEvaluationsScatter",
            contentType:"application/json",
            data : "",
            success: function(resultJSON) {
                if($.trim(resultJSON)) {
                    var result = JSON.parse(resultJSON);
                    var data = {
                        labels: result['labels'],
                        series: result['series']
                    };
                    var options = {
                        showLine: false,
                        axisX: {
                            type: Chartist.FixedScaleAxis,
                            high: 5,
                            low: 0,
                            divisor: 5,
                            onlyInteger: false
                        },
                        plugins: [
                            Chartist.plugins.legend({
                                legendNames: ["1", "2", "3", "4", "5"]
                            }),
                            Chartist.plugins.tooltip()
                        ]
                    };
                    if (result['labels'].length !== 0) {
                        //chart.html("");
                        new Chartist.Line('#chartHours',data, options);
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

});




