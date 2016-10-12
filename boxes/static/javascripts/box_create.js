$(document).ready(function() {
  $("#id_expires_at").datetimepicker({
    format: "Y-m-d H:i"
  });

  $("#id_never_expires").on("change", function(){
    if ($(this).is(":checked")){
      $("#id_expires_at").prop("disabled", true).val("");
    } else {
      $("#id_expires_at").prop("disabled", false);
    }
  });

  $("#box-create-form-js").on("submit", function(){
    var $this = $(this);
    $.ajax({
      url: $this.attr("action"),
      method: $this.attr("method"),
      data: $this.serialize()
    }).done(function(data){
      window.location = data.location;
    }).fail(function(data){
      var fields = ["__all__", "name", "description", "max_messages",
                    "expires_at", "never_expires"];
      var form_errors = data.responseJSON.form_errors;
      for(var i=0;i<fields.length; i++){
        var errorContainer = $("#"+ fields[i] +"-errors-js");
        errorContainer.html("");
        if(form_errors[fields[i]]){
          errorContainer.append("<p>" + form_errors[fields[i]] + "</p>");
        }
      }
    });
    return false;
  });
});
$(".md-modal-xs label").addClass("smalltext");
$(".md-modal-xs input[type=text]").addClass("text padding-modals1");
$(".md-modal-xs input[type=number]").addClass("text padding-modals1");
$(".md-modal-xs textarea").addClass("text padding-modals2");