$(document).ready(function () {
    /* Show modal to confirm user deletion */
    var deleteModal = $('#deleteUser');
    deleteModal.on('show.bs.modal', function (e) {
        var row = $(e.relatedTarget).closest("tr");
        var userId = row.find("input[name='_userId']").val();
        var userName = row.find("td[name='userName']").text();
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
        var userId = row.find("input[name='_userId']").val();
        var enrollmentId = row.find("td[name='enrollmentId']").text();
        var firstName = row.find("input[name='_firstName']").val();
        var lastName = row.find("input[name='_lastName']").val();
        var email = row.find("input[name='_email']").val();
        var role = row.find("input[name='_roleId']").val();
        var department = row.find("input[name='_department']").val();
        $(this).find("input[name='_userId']").val(userId);
        $(this).find("input[name='enrollment_number']").val(enrollmentId);
        $(this).find("input[name='first_name']").val(firstName);
        $(this).find("input[name='last_name']").val(lastName);
        $(this).find("input[name='email']").val(email);
        $(this).find("select[name='role']").val(role);
        if(department !== ""){
            $(this).find("select[name='department']").val(department);
        }
    });
     editModal.find(".btn-primary").on('click', function () {
        editModal.find("form").submit();
    });

    var filter = $('#filter');
     filter.find(".btn").on('click', function () {
         filter.find('form').submit();
     });


});