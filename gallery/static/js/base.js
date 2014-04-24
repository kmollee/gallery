$(function() {

    // Hide messages after a couple seconds.
    // Still undecided if I want to use this.
    //$("#messages").delay(6000).hide("blind", 500);

    function keydownNavigate(direction) {
        selector = $("[data-navigate=" + direction + "]:last");
        if (selector.attr("href")) {
            window.location = selector.attr("href");
        }
    }

    // Handle the keydown navigation for images and albums.
    $(document).keydown(function(event){
        if (event.which == 37 ) (keydownNavigate("left") );
        if (event.which == 39 ) (keydownNavigate("right") );
        if (event.which == 40 ) (keydownNavigate("down") );
        // Only scroll up if we are at the top of the page.
        if (event.which == 38 && $(document).scrollTop() == 0 ) (keydownNavigate("up") );
    });

    // Enabling the modal window shows the wrapper and enables the cancel button.
    function enableModalWindow() {
        $("#modal-wrapper").show();
        $("#modal .cancel").click(function(event){
            disableModalWindow();
        });
        $("#modal select").chosen();
    }

    // Disabling the modal window clears the html and hides the  wrapper.
    function disableModalWindow() {
        $("#modal").html("");
        $("#modal-wrapper").hide();
    }

    // There was a processing error, so log it and alert the user.
    function errorProcessing(data) {
        console.log(data);
        alert("Error processing request. Please try again later.");
    }

    // Initializing the modal form will change the form to an AJAX form
    // and will catch the form resposne and re-populate the div with the
    // results of the form if status is "ERROR". If status is "OK" then the
    // page will be refreshed with the URL that was sent from the server.
    function initializeModalForm() {
        // Change the form in the modal window to an AJAX form.
        $("#modal form").submit(function(event){
            event.preventDefault();
            $.ajax({
                method: "POST",
                url: $(this).attr("action"),
                data: $(this).serialize(),
                success: function(data) {
                    if (data.url) {
                        disableModalWindow();
                        window.location = data.url;
                    }
                    else if (data.html) {
                        $("#modal").html(data.html);
                        enableModalWindow();
                        initializeModalForm();
                    }
                    else {
                        errorProcessing(data);
                    }
                },
                error: function(data){
                    errorProcessing(data);
                }
            });
        });
    }

    // Send an AJAX request when Rotate is clicked.
    $("[data-modal='rotate']").click(function(event){
        event.preventDefault();
        $.ajax({
            method: "POST",
            url: $(this).attr("href"),
            success: function(data){
                // Simply reload the image (which will be rotated).
                // Strip off the previous querystring from the image first.
                img = $(".photo-main .photo img");
                img.attr("src", img.attr("src").split("?")[0] + "?" +
                    new Date().getTime());
            },
            error: function(data){
                errorProcessing(data);
            }
        });
    });

    // Display the form when any modal form links are clicked.
    $("[data-modal='form']").click(function(event){
        event.preventDefault();
        $.getJSON($(this).attr("href"), function(data) {
            if (data.html) {
                $("#modal").html(data.html)
                enableModalWindow();
                initializeModalForm();
                $("#modal input[type='text']:enabled:first").focus();
            }
            else {
                errorProcessing(data);
            }
        });
    });

});
