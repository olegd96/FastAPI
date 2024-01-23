

function loadHTML(url, targetElement) {
    var xmlHttp = new XMLHttpRequest();
    xmlHttp.onreadystatechange = function() {
      if (this.readyState == 4 && this.status == 200) {
        targetElement.innerHTML = this.responseText;
      }
    };
    xmlHttp.open("GET", url, true);
    xmlHttp.send();
  }


async function loginUser() {
    const wrongCredentialsSpan = document.getElementById("wrong_credentials");
    wrongCredentialsSpan.textContent = "";

    const url = "/auth/login";
    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;
    let myDiv = document.getElementById('nav_box');
    await fetch(url, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'}, 
        body: JSON.stringify({email: email, password: password}),
    }).then(response => {
        if (response.status === 200) {
            //window.location.href = "/pages/bookings"
            var url = "/pages/bookings";
            fetch(url)
                .then(response => response.text())
                .then(data => { myDiv.innerHTML = data, htmx.process(myDiv); } );
            cancel("logpanel");
        
        } else {
            wrongCredentialsSpan.textContent = "Неверный email или пароль";
        }
    });
}
