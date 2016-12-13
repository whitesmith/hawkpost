$(document).ready(function() {
  /*
    On click copy the box link to the clipboard
  */
  $(".box-options").click(function(){
    $(this).submit();
  });
  $(".copy-to-clipboard-js").on("click", function(){
    $this = $(this);
    var previousText = $this.html();
    var input = $("#" + $this.attr("data-src"));
    input.select();
    try{
      var result = document.execCommand('copy');
      if(result){
        $this.html("URL copied");
      } else {
        $this.html("Unable to copy to clipboard");
      }
      setTimeout(function(){
        $this.html(previousText);
      }, 1500);
    } catch (err) {
      //Browser does not support "copy"?
      $this.html("Unable to copy to clipboard");
      $(".copy-to-clipboard-js").prop("disabled", true);
    }
  });
});
