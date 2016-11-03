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

  $(".form__block label").addClass("smalltext");
  $(".form__block input[type=text]").addClass("text padding-settings");


  $("#tab1").click(function(){
    //slide up all the link lists
    $("#section1").slideDown();
    $("#section2").slideUp();
    $("#section3").slideUp();
    $("#tab1").addClass("active");
    $("#tab2").removeClass("active");
    $("#tab3").removeClass("active");
  });
  $("#tab2").click(function(){
    //slide up all the link lists
    $("#section2").slideDown();
    $("#section1").slideUp();
    $("#section3").slideUp();
    $("#tab2").addClass("active");
    $("#tab1").removeClass("active");
    $("#tab3").removeClass("active");
  });
  $("#tab3").click(function(){
    //slide up all the link lists
    $("#section3").slideDown();
    $("#section1").slideUp();
    $("#section2").slideUp();
    $("#tab3").addClass("active");
    $("#tab1").removeClass("active");
    $("#tab2").removeClass("active");
  });
  $('.radio_button').on('change', function() {
    if ($('.radio_button:checked').val() == "keyserver") {
      $("#keyserver_url").slideDown();
      $("#public_key").slideUp();
    } else {
      $("#keyserver_url").slideUp();
      $("#public_key").slideDown();
    }
  });
});

