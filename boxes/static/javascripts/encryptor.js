function encrypt() {
	var options = {
	    data: $("#id_message").val(),
	    publicKeys: openpgp.key.readArmored($(".public-key-js").html()).keys
	};

	openpgp.encrypt(options).then(function(ciphertext) {
	    var $box = $("#box")
      $("#id_message").val(ciphertext.data);
      $box.unbind("submit");
      $box.submit();
	});
  return false
}

window.onload = function() {
    $("#box").on("submit", encrypt)
}
