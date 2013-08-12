(function() {
	function generateHash() {
		// fetch master password and then clear field
		var seed = $("#seed").val();
		var keyword = $("#keyword").val();

		// clear the seed each time a hash is generated
		$("#seed").val("");

		var hashpass = b64_hmac_sha1(seed, keyword).substr(0,16);

		$("#result").val(hashpass).select();

		return false;
	}

	$("form").on("submit", function(e) {
		return generateHash();
	});
}());
