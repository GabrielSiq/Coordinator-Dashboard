
function updateChart(content) {
    var paramSet = {};
    var hasAny = false;
    content.find(".row.param").each(function () {
        var params = {};
        $(this).find("select.form-control").each(function () {
            params[$(this).attr("id")] = $(this).val();
            if(hasAny === false && $(this).val() !== ""){
                hasAny = true;
            }
       });
        paramSet[$(this).attr("id")] = params;
    });
    var requestJSON = {"chartId" : content.parent().attr("id"), "requestParams" : paramSet};
    var chart = content.find(".ct-chart, .table-striped");
    var chartId = chart.attr("id");
    var message = chart.siblings("div.message");
    if(hasAny){
        $.ajax({
            type: "POST",
            url: "/getChartData",
            contentType:"application/json",
            data : JSON.stringify(requestJSON),
            success: function(resultJSON) {
                if($.trim(resultJSON)) {
                    var result = JSON.parse(resultJSON);
                    for(var key in result){

                    }
                    var data = {
                        labels: result['labels'],
                        series: [result['series']]
                    };
                    var options = {
                        lineSmooth: false
                    };
                    if (result['labels'].length !== 0) {
                        chart.html("");
                        new Chartist.Line("#" + chartId, data, options);
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

$(document).ready(function(){
    // Load saved configs into dropdown
    var dataStore = {};
    $(".query-controls").each(function() {
        var controls = $(this);
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
                for (var key in savedQueries) {
                    queryName.append($('<option>', {
                        value: key,
                        text: savedQueries[key].name
                    }));
                }
            },
            error: function(){
                alert("error");
            }
        });
    });
    $(".query-controls select[name='queryName']").change(function(){
        var select = $(this);
        var card = select.closest("div.card");
        if (select.val()) {
            var queryData = JSON.parse(JSON.parse(dataStore[card.attr("id")])[select.val().toString()]['query_data']);
            for (var key in queryData) {
                card.find("select#" + key).val(queryData[key]);
            }
            updateChart(card.find(".content"))
        }
    });
    $("select.combobox").change(function() {
        updateChart($(this).closest(".content"));
    });
    $(".card form").on('click', 'div.row button.clear', function () {
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
        updateChart($(this).closest('.content'));
    });
    $(".card form button.add").click(function () {
        var prevRow = $(this).closest('.row').prev();
        var newRow = prevRow.clone();
        rowId = parseInt(newRow.attr("id").slice(3)) + 1;
        newRow.attr("id", "row" + rowId);
        newRow.insertAfter(prevRow);
    });
});




