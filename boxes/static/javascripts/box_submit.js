$(document).ready(function () {
  /*
   * Encrypt the current form content
   */
  function encryptContent() {
    var serverSigned = $('.server-signed-js').text() === 'True';
    var contentType = serverSigned ? 'Content-Type: text/plain\n\n' : '';

    var options = {
      data: contentType + $("#id_plain").val(),
      /* Works for one key, need to change when multiple recipients is available */
      publicKeys: openpgp.key.readArmored($(".public-key-js").html()).keys
    };

    openpgp.encrypt(options).then(function (ciphertext) {
      var $box = $("#box");

      $("#id_message").val(ciphertext.data);

      if (quickCheckFormContent()) {
        $box.submit();
      } else {
        alert("Well, encryption doesn't seem to be as it should. Try again.");
      }
    });

    return false;
  }

  /*
   * Might be useless but
   * Check that the content is really encrypted before submitting
   */
  function quickCheckFormContent() {
    var begin = "-----BEGIN PGP MESSAGE-----";
    var end = "-----END PGP MESSAGE-----";

    var message = $("#id_message").val();
    var lines = message.split("\n");

    if (lines[0] !== begin || lines[lines.length - 2] !== end) {
      return false;
    }

    return true;
  }

  /*
   * Only when javascript is enabled, the form is created.
   */
  function createBox() {
    var $formDiv = $(".form-div-js");

    /* Hidden form fields */
    var csrfToken = $formDiv.attr("data-csrf-token");
    var action = $formDiv.attr("data-action");

    var $form = $("<form></form>");
    $form.attr('id', "box").attr("action", action)
    $form.attr("method", "post");

    var $csrfTokenField = $("<input type='hidden' name='csrfmiddlewaretoken'></input>");
    $csrfTokenField.val(csrfToken);
    $form.append($csrfTokenField);

    var $encryptedMessage = $("<input id='id_message' name='message' type='hidden'></input>");
    $form.append($encryptedMessage);

    $formDiv.append($form);

    /* Input fields */
    var $inputDiv = $("<div></div>");
    $inputDiv.addClass("form__wrap_msg link-box__box");

    var $label = $("<label for='id_plain'></label>");
    var $textArea = $("<textarea id='id_plain' cols='40' rows='10'></textarea>");
    $textArea.attr("placeholder", "All the contents, inserted into this box, will be encrypted with " +
                                  "the recipient's public key before leaving this computer.")

    $inputDiv.append($("<p class='no-margin-top'></p>").append($label).append($textArea));
    $inputDiv.append($("<a id='encrypt-action-js' class='btn-blue smalltext u-blockify'>Encrypt and Send</a>"));

    $formDiv.append($inputDiv);

    $("#encrypt-action-js").on("click", encryptContent);
  }

  /*
   * Show introduction tooltip on click
   */
  $(".hawkpost__block").click(function () {
    $(this).toggleClass("open__hawkpost__text");
    $(".hawkpost__block").not(this).removeClass("open__hawkpost__text");
  });

  createBox();
});
