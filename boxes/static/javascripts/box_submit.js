$(document).ready(function () {
  /*
   * Encrypt the current form content
   */
  var MAX_MSG_SIZE = 5242880; // ~ 5 Mb

  function encryptContent(){
    var content;
    var contentType;
    var contentFromFile = $("#id_source").is(':checked');

    if (contentFromFile) {
      var file = $('#id_file_select')[0].files[0];
      var reader = new FileReader();
      reader.onload = function(evt) {
        content = new Uint8Array(evt.target.result);
        encryptAndSend(content, file.name);
      };
      reader.readAsArrayBuffer(file);

    } else {
      content = $("#id_plain").val();
      encryptAndSend(content, null);
    }
    return false;
  }

  function encryptAndSend(content, fileName) {
    var options = {
      data: content,
      /* Works for one key, need to change when multiple recipients is available */
      publicKeys: openpgp.key.readArmored($(".public-key-js").html()).keys
    };

    openpgp.encrypt(options).then(function (ciphertext) {
      var $box = $("#box");

      $("#id_message").val(ciphertext.data);
      if (fileName){
        $("#id_file_name").val(fileName + ".asc");
      }

      /* Also update the input box's message as a visual cue
       * that it has been sent after being encrypted. */
      $("#id_plain").val(ciphertext.data);

      if (quickCheckFormContent()) {
        $box.submit();
      } else {
        alert("Well, encryption doesn't seem to be as it should. Try again.");
      }
    });
  }

  /*
   * Shows / Hides the input forms for the diferent formats (Text/File)
   */
  function changeSource(){
    var $source = $("#id_source");
    if ($source.is(':checked')){
      $('#id_plain').hide();
      $('#id_plain_label').hide();
      $('#id_plain_paragraph').hide();
      $('#id_file_select').show();
      $('#id_file_select_label').show();
      checkFileSize();
    } else {
      $('#id_file_select').hide();
      $('#id_file_select_label').hide();
      $('#id_plain').show();
      $('#id_plain_label').show();
      $('#id_plain_paragraph').show();
      checkMessageSize();
    }
  }

  /*
   * Check if select file size is within the allowed limits
   */
  function checkFileSize(){
    var selectedFile = $('#id_file_select')[0].files[0];
    var $notificationBox = $("#id_notification");
    var $sendButton = $("#encrypt-action-js");
    if(selectedFile && selectedFile.size < MAX_MSG_SIZE){
      $notificationBox.html("");
      $sendButton.show();
    } else {
      $notificationBox.html("Please select a file smaller than 5Mb.");
      $sendButton.hide();
    }
  }

  function checkMessageSize(){
    var msg = $('#id_plain');
    var messageBytes = (new TextEncoder('utf-8').encode(msg.val())).length;
    var $notificationBox = $("#id_notification");
    var $sendButton = $("#encrypt-action-js");
    if (messageBytes < MAX_MSG_SIZE) {
      $notificationBox.html("");
      $sendButton.show();
    } else {
      $notificationBox.html("Your message cannot excceed 5Mb.");
      $sendButton.hide();
    }
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
    var authenticated_user = $("#authenticated_user").length
    var $formDiv = $(".form-div-js");

    /* Hidden form fields */
    var csrfToken = $formDiv.attr("data-csrf-token");
    var action = $formDiv.attr("data-action");

    var $form = $("<form></form>");
    $form.attr('id', "box").attr("action", action);
    $form.attr("method", "post");

    var $csrfTokenField = $("<input type='hidden' name='csrfmiddlewaretoken'></input>");
    $csrfTokenField.val(csrfToken);
    $form.append($csrfTokenField);

    var $fileName = $("<input id='id_file_name' name='file_name' type='hidden'></input>");
    $form.append($fileName);

    var $encryptedMessage = $("<input id='id_message' name='message' type='hidden'></input>");
    $form.append($encryptedMessage);

    if (authenticated_user) {
      var $replyLabel = $("<label id='id_reply_label' for='id_add_reply_to'>Add own email to ReplyTo</label>");
      var $replyInput = $("<input class='box_submit_input' id='id_add_reply_to' name='add_reply_to' type='checkbox'></input>");
      var $replyGroup = $("<div class='box_submit_checkbox'></div>").append($replyLabel).append($replyInput);
      $form.append($replyGroup);
    }

    $formDiv.append($form);

    /* Input fields */
    var $inputDiv = $("<div></div>");
    $inputDiv.addClass("form__wrap_msg link-box__box");

    var $sourceLabel = $("<label id='id_source_label' for='id_source'>Send local file</label>");
    var $sourceInput = $("<input class='box_submit_input' id='id_source' type='checkbox'></input>");
    var $sourceGroup = $("<div class='box_submit_checkbox'></div>").append($sourceLabel).append($sourceInput);

    var $label = $("<label id='id_plain_label' for='id_plain'></label>");
    var $textArea = $("<textarea id='id_plain' cols='40' rows='10'></textarea>");
    $textArea.attr("placeholder", "All the contents, inserted into this box, will be encrypted with " +
                                  "the recipient's public key before leaving this computer.");
    var $paragraph = $("<p id='id_plain_paragraph' for='id_source'>Or</p>");
    var $messageGroup = $("<div></div>").append($label).append($textArea).append($paragraph);

    var $fileSelectLabel = $("<label id='id_file_select_label' for='id_file'></label>");
    var $fileSelectInput = $("<input class='box_submit_file' id='id_file_select' type='file'></input>");
    var $fileSelectGroup = $("<div></div>").append($fileSelectLabel).append($fileSelectInput);

    $inputDiv.append($("<p class='no-margin'></p>").append($messageGroup).append($sourceGroup).append($fileSelectGroup));
    $inputDiv.append($("<p class='smalltext no-margin-top' id='id_notification'></p>"));
    $inputDiv.append($("<a id='encrypt-action-js' class='btn-blue smalltext u-blockify'>Encrypt and Send</a>"));

    $formDiv.append($inputDiv);

    changeSource();
    $("#id_source").on('change', changeSource);
    $("#encrypt-action-js").on("click", encryptContent);
    $('#id_file_select').on('change', checkFileSize);
    $('#id_plain').on('keyup', checkMessageSize);
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
