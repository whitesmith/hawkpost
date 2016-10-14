$(document).ready(function(){
  if($("#id_keyserver_url").val().length != 0) {
    $("#id_public_key").attr("disabled",true);
  }
  else if($("#id_public_key").val().length != 0) {
    $("#id_keyserver_url").attr("disabled",true);
  }

  $("#id_keyserver_url").on("input",function(){
    if($("#id_keyserver_url").val().length == 0) {
      $("#id_public_key").attr("disabled",false);
    } else {
      $("#id_public_key").attr("disabled",true);
    }
  });

  $("#id_public_key").on("input",function(){
    if($("#id_public_key").val().length == 0) {
      $("#id_keyserver_url").attr("disabled",false);
    } else {
      $("#id_keyserver_url").attr("disabled",true);
    }
  });

  $(".form__block label").addClass("smalltext");
  $(".form__block input[type=text]").addClass("text padding-settings");

  $("#id_server_signed").change(function() {
    $('.server-signed-info-js .popuptext').toggleClass('show');
  });
});

