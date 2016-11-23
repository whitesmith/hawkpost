$(document).ready(function(){
  $(".form__block label").addClass("smallmedium text-darkest");
  $(".form__block input[type=text]").addClass("text padding-settings");
  $(".form__block textarea").addClass("xsmalltext");
  $(".label-form-b label").addClass("smallmedium text-darkest");
  $(".checkbox- label").addClass("smallmedium text-darkest");

  $("#tab1").click(function(){
    //slide up all the link lists
    $("#section1").show();
    $("#section2").hide();
    $("#section3").hide();
    $("#tab1").addClass("active");
    $("#tab2").removeClass("active");
    $("#tab3").removeClass("active");
  });
  $("#tab2").click(function(){
    //slide up all the link lists
    $("#section2").show();
    $("#section1").hide();
    $("#section3").hide();
    $("#tab2").addClass("active");
    $("#tab1").removeClass("active");
    $("#tab3").removeClass("active");
  });
  $("#tab3").click(function(){
    //slide up all the link lists
    $("#section3").show();
    $("#section1").hide();
    $("#section2").hide();
    $("#tab3").addClass("active");
    $("#tab1").removeClass("active");
    $("#tab2").removeClass("active");
  });
  $('.radio_button').on('change', function() {
    if ($('.radio_button:checked').val() == "keyserver") {
      $("#keyserver_url").show();
      $("#public_key").hide();
      $("#id_public_key").val('');
    } else {
      $("#keyserver_url").hide();
      $("#public_key").show();
      $("#id_keyserver_url").val('');
    }
  });
  if($("#id_public_key").val().length == 0  && $("#id_keyserver_url").val().length != 0) {
    $("#keyserver_option").prop("checked", true);
    $("#keyserver_url").show();
    $("#public_key").hide();
    $("#id_public_key").val('');
  }
  
  $(".errorlist").each(function(){
    if ($("li",this).length >= 1) {
      index = $(this).closest(".section").index();
      if(index == 0) {
        $("#tab1").click();
      } else if(index == 1) {
        $("#tab2").click();
      } else {
        $("#tab3").click();
      }
      return;
    }
  });
});

