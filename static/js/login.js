function showPassword(fieldId) {
    var passwordField = document.getElementById(fieldId);
    var showCursorId = '';
    if (fieldId === 'secret_key') {
        showCursorId = 'showCursor'
    } else if (fieldId === 'kms_key_id') {
        showCursorId = 'showCursorKMS'
    }
    var showCursor = document.getElementById(showCursorId);

    if (passwordField.type === "password") {
        passwordField.type = "text";
        showCursor.classList.remove("fa-eye-slash");
        showCursor.classList.add("fa-eye");
    } else {
        passwordField.type = "password";
        showCursor.classList.remove("fa-eye");
        showCursor.classList.add("fa-eye-slash");
    }
}