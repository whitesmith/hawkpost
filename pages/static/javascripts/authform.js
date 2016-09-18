$(document).ready(function(){
  $("#login-form-js").on("submit", function(){
    var $this = $(this);
    $.ajax({
      url: $this.attr("action"),
      method: $this.attr("method"),
      data: $this.serialize()
    }).done(function(data){
      document.location = data.location
    }).fail(function(data){
      var errorContainer = $("#login-form-errors-js");
      errorContainer.html("");
      var errors = [];
      var form_errors = data.responseJSON.form_errors;
      if(form_errors.__all__){
        errors = errors.concat(form_errors.__all__);
      }
      if(form_errors.email){
        errors = errors.concat(form_errors.email);
      }
      if(form_errors.password){
        errors = errors.concat(form_errors.password);
      }
      for(var i=0;i<errors.length;i++){
        errorContainer.append("<p>" + errors[i] + "</p>");
      }
    })
    return false;
  });

  $("#signup-form-js").on("submit", function(){
    var $this = $(this)
    $.ajax({
      url: $this.attr("action"),
      method: $this.attr("method"),
      data: $this.serialize()
    }).done(function(data){
      document.location = data.location
    }).fail(function(data){
      var errorContainer = $("#signup-form-errors-js");
      errorContainer.html("");
      var errors = [];
      var form_errors = data.responseJSON.form_errors;
      if(form_errors.__all__){
        errors = errors.concat(form_errors.__all__);
      }
      if(form_errors.email){
        errors = errors.concat(form_errors.email);
      }
      if(form_errors.password1){
        errors = errors.concat(form_errors.password1);
      }
      if(form_errors.password2){
        errors = errors.concat(form_errors.password2);
      }
      for(var i=0;i<errors.length;i++){
        errorContainer.append("<p>" + errors[i] + "</p>");
      }
    })
    return false;
  });

  if(window.location.href.indexOf('#modal-login') != -1) {
    $(".md-show").css('visibility', 'visible');
  }
});
