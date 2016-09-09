$(document).ready(function(){
  $("#login-form-js").on("submit", function(){
    var $this = $(this)
    $.ajax({
      url: $this.attr("action"),
      method: $this.attr("method"),
      data: $this.serialize()
    }).done(function(data){
      document.location = data.location
    }).fail(function(data){
      var errorContainer = $("#login-form-errors-js");
      errorContainer.html("");
      var errors = []
      if(data.responseJSON.form_errors.__all__)
        errors = errors.concat(data.responseJSON.form_errors.__all__);
      if(data.responseJSON.form_errors.email)
        errors = errors.concat(data.responseJSON.form_errors.email);
      if(data.responseJSON.form_errors.password)
        errors = errors.concat(data.responseJSON.form_errors.password);
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
      var errors = []
      if(data.responseJSON.form_errors.__all__)
        errors = errors.concat(data.responseJSON.form_errors.__all__);
      if(data.responseJSON.form_errors.email)
        errors = errors.concat(data.responseJSON.form_errors.email);
      if(data.responseJSON.form_errors.password1)
        errors = errors.concat(data.responseJSON.form_errors.password1);
      if(data.responseJSON.form_errors.password2)
        errors = errors.concat(data.responseJSON.form_errors.password2);
      for(var i=0;i<errors.length;i++){
        errorContainer.append("<p>" + errors[i] + "</p>");
      }
    })
    return false;
  });
});
