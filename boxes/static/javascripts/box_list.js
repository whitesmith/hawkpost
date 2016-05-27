$(document).ready(function() {
  /*
    On click copy the box link to the clipboard
  */
  $(".copy-to-clipboard-js").on("click", function(){
    $this = $(this);
    var previousText = $this.text();
    var input = $("#" + $this.attr("data-src"));
    input.select();
    try{
      var result = document.execCommand('copy');
      if(result){
        $this.text("URL copied with success");
      } else {
        $this.text("Unable to copy to clipboard");
      }
      setTimeout(function(){
        $this.text(previousText);
      }, 1500);
    } catch (err) {
      //Browser does not support "copy"?
      $this.text("Unable to copy to clipboard");
      $(".copy-to-clipboard-js").prop("disabled", true);
    }
  });
});
