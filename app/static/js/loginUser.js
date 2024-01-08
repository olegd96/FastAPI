
        async function loginUser() {
            const wrongCredentialsSpan = document.getElementById("wrong_credentials");
            wrongCredentialsSpan.textContent = "";

            const url = "http://localhost:8000/auth/login";
            const email = document.getElementById("email").value;
            const password = document.getElementById("password").value;

            await fetch(url, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'}, 
                body: JSON.stringify({email: email, password: password}),
            }).then(response => {
                if (response.status === 200) {
                    window.location.href = "/pages/bookings"
                
                } else {
                    wrongCredentialsSpan.textContent = "Неверный email или пароль";
                }
            });
        }
