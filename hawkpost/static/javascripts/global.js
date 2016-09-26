$(document).ready(function(){
  setTimeout(function(){
    $(".messages-elem-js").remove();
  }, 3000);

  /*
    On user settings page, open the tooltips/popups
  */
  $(".server-signed-info-js").on("click", function () {
    var popup = document.getElementById('server-signed-content-js');
    popup.classList.toggle('show');
  })

  $(".keys-help-popup-js").on("click", function () {
    var popup = document.getElementById('keys-help-content-js');
    popup.classList.toggle('show');
  })
});
