$(document).ready(function(){
  $("#login-form-js").on("submit", function(){
    var $this = $(this);
    $.ajax({
      url: $this.attr("action"),
      method: $this.attr("method"),
      data: $this.serialize()
    }).done(function(data){
      document.location = data.location;
    }).fail(function(data){
      var errorContainer = $("#login-form-errors-js");
      errorContainer.html("");
      if (data.status === 400){
        var errors = data.responseJSON.form.errors;
        var form_fields = data.responseJSON.form.fields;
        if(form_fields.login.errors){
          errors = errors.concat(form_fields.login.errors);
        }
        if(form_fields.password.errors){
          errors = errors.concat(form_fields.password.errors);
        }
        for(var i=0;i<errors.length;i++){
          errorContainer.append("<p class='text-warning'>" + errors[i] + "</p>");
        }
      } else if (data.status === 403){
        var msg = "Too many failed attempts. The account is locked for 1 hour. Please try again later.";
        errorContainer.append("<p class='text-warning'>"+ msg +"</p>");
      }
    });
    return false;
  });

  $("#signup-form-js").on("submit", function(){
    var $this = $(this);
    $.ajax({
      url: $this.attr("action"),
      method: $this.attr("method"),
      data: $this.serialize()
    }).done(function(data){
      document.location = data.location;
    }).fail(function(data){
      var errorContainer = $("#signup-form-errors-js");
      errorContainer.html("");
      var errors = data.responseJSON.form.errors;
      var form_fields = data.responseJSON.form.fields;
      if(form_fields.email.errors){
        errors = errors.concat(form_fields.email.errors);
      }
      if(form_fields.password1.errors){
        errors = errors.concat(form_fields.password1.errors);
      }
      if(form_fields.password2.errors){
        errors = errors.concat(form_fields.password2.errors);
      }
      for(var i=0;i<errors.length;i++){
        errorContainer.append("<p class='text-warning'>" + errors[i] + "</p>");
      }
    });
    return false;
  });

  if(window.location.href.indexOf('#modal-login') != -1) {
    $(".md-show").css('visibility', 'visible');
  }
});
