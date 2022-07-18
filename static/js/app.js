document.getElementsByTagName("form")[0].addEventListener("submit", function(e) {
	// fetch master password and then clear field
	var seed = document.getElementById("seed").value;
	var keyword = document.getElementById("keyword").value;

	// clear the seed each time a hash is generated
	document.getElementById("seed").value = "";

	var hashpass = b64_hmac_sha1(seed, keyword).substr(0,16);

	document.getElementById("result").value = hashpass;
	document.getElementById("result").select();

	e.preventDefault();
});