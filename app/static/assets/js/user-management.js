$(document).ready(function () {
    /* Show modal to confirm user deletion */
    var deleteModal = $('#deleteUser');
    deleteModal.on('show.bs.modal', function (e) {
        var row = $(e.relatedTarget).closest("tr");
        var card = row.closest(".card");
        var userId = row.find("td").eq(0).text();
        var userName = row.find("td").eq(1).text();
        $(this).find("input[name='_userId']").val(userId);
        $(this).find("#deleteUserName").text(userName);
    });
    /* Deletes user */
    deleteModal.find(".btn-danger").on('click', function () {
        deleteModal.find("form").submit();
    });
});