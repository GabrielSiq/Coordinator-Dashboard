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
    var editModal = $('#editUser');
    editModal.on('show.bs.modal', function (e) {
        var row = $(e.relatedTarget).closest("tr");
        var userId = row.find("td").eq(0).text();
        var firstName = row.find("input[name='_firstName']").val();
        var lastName = row.find("input[name='_lastName']").val();
        var email = row.find("input[name='_email']").val();
        var role = row.find("input[name='_roleId']").val();
        $(this).find("input[name='_userId']").val(userId);
        $(this).find("input[name='first_name']").val(firstName);
        $(this).find("input[name='last_name']").val(lastName);
        $(this).find("input[name='email']").val(email);
        $(this).find("select[name='role']").val(role);
    });
     editModal.find(".btn-primary").on('click', function () {
        editModal.find("form").submit();
    })

});