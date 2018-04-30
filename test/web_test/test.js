function submit_creds() {
    var un = document.getElementById('username').value;
    var pw = document.getElementById('password').value;

    var request = new XMLHttpRequest();
    request.open("GET", "http://localhost:4500/cpslo/authorize", false);
    request.setRequestHeader("Authorization", "Basic " + btoa(un + ":" + pw));
    request.send(null)
}
