$(document).ready(function() {
    // Auto-dismiss the flash message after 3 seconds
    setTimeout(function() {
        $(".flash-message").fadeOut('slow');
    }, 3000);

    // Allow the flash message to be closed when the close button is clicked
    $(".flash-message .close").on("click", function() {
        $(this).parent().fadeOut('slow');
    });
});
