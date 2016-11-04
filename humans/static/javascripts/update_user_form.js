$(document).ready(function(){
  

  $(".form__block label").addClass("smalltext");
  $(".form__block input[type=text]").addClass("text padding-settings");


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
      $("#public_key").val('')
    } else {
      $("#keyserver_url").hide();
      $("#public_key").show();
      $("#keyserver_url").val('')
    }
  });
});

