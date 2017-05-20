$(document).ready(function () {
    /* Show modal to confirm user deletion */
    var deleteModal = $('#deleteInvite');
    deleteModal.on('show.bs.modal', function (e) {
        var row = $(e.relatedTarget).closest("tr");
        var inviteId = row.find("input[name='_invitationId']").val();
        var inviteEmail = row.find("td[name='email']").text();
        $(this).find("input[name='_inviteId']").val(inviteId);
        $(this).find("#deleteInviteEmail").text(inviteEmail);
    });
    /* Deletes user */
    deleteModal.find(".btn-danger").on('click', function () {
        deleteModal.find("form").submit();
    });
});