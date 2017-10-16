$(document).ready(function(){
  $(".form__block label").addClass("smallmedium text-darkest");
  $(".form__block input[type=text]").addClass("text padding-settings");
  $(".form__block textarea").addClass("xsmalltext");
  $(".label-form-b label").addClass("smallmedium text-darkest");
  $(".checkbox- label").addClass("smallmedium text-darkest");

  $(".sett__nav__item").click(function(evt) {
    var tabId = evt.target.id;
    var index = $(evt.target).index() + 1;

    $(".sett__nav__item").removeClass("active");
    $(tabId).addClass("active");
    $(".section").hide();
    $("#section" + index).show();
  });

  $('.radio_button').on('change', function() {
    if ($('.radio_button:checked').val() == "keyserver") {
      $("#keyserver_url").show();
      $("#public_key").hide();
    } else {
      $("#keyserver_url").hide();
      $("#public_key").show();
    }
  });
  if($("#id_keyserver_url").val().length != 0) {
    $("#keyserver_option").prop("checked", true);
    $("#keyserver_url").show();
    $("#public_key").hide();
  }
  $("#form").submit(function(event){
    if ($('.radio_button:checked').val() == "keyserver") {
      $("#id_public_key").val('');
      $("#id_public_key").text('');
    } else {
      $("#id_keyserver_url").val('');
      $("#id_keyserver_url").text('');
    }
  });
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

