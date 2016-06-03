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
});
