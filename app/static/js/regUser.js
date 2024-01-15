async function regUser() {
    const wrongCredentialsSpan = document.getElementById("wrong_credentials");
    wrongCredentialsSpan.textContent = "";
    let email_pole = document.getElementById("email");
    let password_pole = document.getElementById("password");
    let button = document.getElementById("log_button");
    let l_pass = document.getElementById("l_pass");
    let l_em = document.getElementById("l_em");
    const url = "http://localhost:8000/auth/register";
    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;
    if (email=="" || password=="") {
        wrongCredentialsSpan.textContent = "Не введён email или пароль";
    } 
    else {
    await fetch(url, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'}, 
        body: JSON.stringify({email: email, password: password}),
    }).then(response => {
        if (response.status === 200) {
            wrongCredentialsSpan.textContent = "Вы зарегистрированы. Войдите в систему.";
            button.style.display = "none";
            email_pole.style.display = "none";
            password_pole.style.display = "none";
            l_pass.style.display = "none";
            l_em.style.display = "none";
        } else if (response.status === 409) {
            wrongCredentialsSpan.textContent = "Пользователь с таким логином уже существует";
        } else {
            wrongCredentialsSpan.textContent = "Ошибка регистрации";
        }
    });
}
}