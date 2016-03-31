function encrypt() {
	var options = {
	    data: $("#id_message").val(),
	    publicKeys: openpgp.key.readArmored($(".public-key-js").html()).keys
	};

	openpgp.encrypt(options).then(function(ciphertext) {
	    console.log(ciphertext.data);
	});
}

window.onload = function() {
    var box = $("#box");
    box.submit(encrypt);
}
