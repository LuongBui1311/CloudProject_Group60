$(document).ready(function () {
    $('#fileTable').dataTable({
        "pageLength": 2,
        "lengthMenu": [2, 3, 10, 25, 50, 100],
        "columnDefs": [
            {"width": "70%", "targets": 0},
            {"width": "30%", "targets": 0}
        ]
    });
});