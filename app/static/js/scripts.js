
async function add_booking(room_id, hotel_id, block_id) {
    const url = "/bookings";
    const date_from = document.getElementById("date_from").value;
    const date_to = document.getElementById("date_to").value;
    let myDiv = document.getElementById('nav_box');
    let myDiv_1 = document.getElementById(block_id);
    await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            room_id: room_id,
            date_from: date_from,
            date_to: date_to
        }),
    }).then(response => {
        if (response.status === 200) {

            alert("Номер добавлен в корзину");

            var url_1 = '/pages/hotels/' + hotel_id + '/rooms?date_from=' + date_from + '&date_to=' + date_to;
            fetch('/pages/bookings', {headers: { 'myHeader': 'true' }})
                .then(response => response.text())
                .then(data => { myDiv.innerHTML = data, htmx.process(myDiv); });
            fetch(url_1)
                .then(response => response.text())
                .then(data => { myDiv_1.innerHTML = data, htmx.process(myDiv_1); });

        }

        else if (response.status === 409) {
            alert("Не осталось свободных номеров");
        }

        else if (response.status === 401) {
            fetch(url, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    room_id: room_id,
                    date_from: date_from,
                    date_to: date_to
                }),
            }).then(response => {
                if (response.status === 200) {

                    alert("Номер добавлен в корзину");

                    var url_1 = '/pages/hotels/' + hotel_id + '/rooms?date_from=' + date_from + '&date_to=' + date_to;
                    fetch('pages/bookings', {headers: { 'myHeader': 'true' }})
                        .then(response => response.text())
                        .then(data => { myDiv.innerHTML = data, htmx.process(myDiv); });
                    fetch(url_1)
                        .then(response => response.text())
                        .then(data => { myDiv_1.innerHTML = data, htmx.process(myDiv_1); });

                }
            }

            );
        }

    });
    refresh_nav();
}


function cancel(val) {
    let obj = document.getElementById(val);
    obj.style.display = "none";
}


async function loginUser() {
    const wrongCredentialsSpan = document.getElementById("wrong_credentials");
    wrongCredentialsSpan.textContent = "";

    const url = "/auth/login";

    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;
    let formBody = [];
    formBody.push('username' + '=' + email);
    formBody.push('password' + '=' + password);
    formBody = formBody.join("&");
    let myDiv = document.getElementById('nav_box');

    await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded'},
        body: formBody
    }).then(response => {
        if (response.status === 200) {
            //window.location.href = "/pages/bookings"
            var url = "/pages/bookings";
            fetch(url, {headers: { 'myHeader': 'true' }})
                .then(response => response.text())
                .then(data => { myDiv.innerHTML = data, htmx.process(myDiv); });
            cancel("logpanel");
            refresh_panel();

        } else {
            wrongCredentialsSpan.textContent = "Неверный email или пароль";
        }
    });
}


async function logoutUser() {
    const url = "/auth/logout";

    await fetch(url, {
        method: 'POST',
    }).then(response => {
        if (response.status === 200) {
            window.location.href = "/pages"
        }
    });
}


async function regUser() {
    const wrongCredentialsSpan = document.getElementById("wrong_credentials");
    wrongCredentialsSpan.textContent = "";
    let email_pole = document.getElementById("email");
    let password_pole = document.getElementById("password");
    let button = document.getElementById("log_button");
    let l_pass = document.getElementById("l_pass");
    let l_em = document.getElementById("l_em");
    const url = "/auth/register";
    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;
    if (email == "" || password == "") {
        wrongCredentialsSpan.textContent = "Не введён email или пароль";
    }
    else {
        await fetch(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json'},
            body: JSON.stringify({ email: email, password: password }),
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

//переписано
async function refresh_nav() {
    let myDiv = document.getElementById('nav_box');
    fetch('/pages/bookings', {headers: { 'myHeader': 'true' }})
        .then(response => {
            if (response.status === 200) {            
                (response.text())
                .then(data => { myDiv.innerHTML = data, htmx.process(myDiv); });}
            else {
                fetch('auth/refresh', {method: 'POST'})
                .then(response => {
                    if (response.status === 200) {
                        fetch('/pages/bookings', {headers: { 'myHeader': 'true' }})
                        .then(response => {
                            if (response.status === 200) {            
                                (response.text())
                                .then(data => { myDiv.innerHTML = data, htmx.process(myDiv); });}                   
                })
            }})
}
})
}


async function refresh_anon_nav() {
    let myDiv = document.getElementById('nav_box');
    fetch('/pages/anon_bookings', {headers: { 'myHeader': 'true' }})
        .then(response => response.text())
        .then(data => { myDiv.innerHTML = data, htmx.process(myDiv); });
}

//переписано
async function refresh_my_bookings() {
    let myDiv = document.getElementById('bookings_list');
    fetch('/pages/my_bookings', {headers: { 'myHeader': 'true' }})
    .then(response => {
        if (response.status === 200) {            
    (response.text())
    .then(data => { myDiv.innerHTML = data, htmx.process(myDiv); });}
})
}

//переписано
async function refresh_my_cart() {
    let myDiv = document.getElementById('bookings_list');
    fetch('/pages/cart', {headers: { 'myHeader': 'true' }})
    .then(response => {
        if (response.status === 200) {            
    (response.text())
    .then(data => { myDiv.innerHTML = data, htmx.process(myDiv); });}
})
}

async function refresh_panel() {
    let myDiv = document.getElementById('anon_cart');
    let myDiv_1 = document.getElementById('bookings_list');
    if (myDiv != null) {
        fetch('/pages/cart', {headers: { 'myHeader': 'true' }})
            .then(response => response.text())
            .then(data => { myDiv.innerHTML = data, htmx.process(myDiv_1); });
    }
}

async function refresh_anon_cart() {
    let myDiv = document.getElementById('bookings_list');
    fetch('/pages/cart/anon', {headers: { 'myHeader': 'true' }})
        .then(response => response.text())
        .then(data => { myDiv.innerHTML = data, htmx.process(myDiv); });
}



async function add_cart(room_id, hotel_id, block_id) {
    const url = "/cart";
    const date_from = document.getElementById("date_from").value;
    const date_to = document.getElementById("date_to").value;
    let myDiv = document.getElementById('nav_box');
    let myDiv_1 = document.getElementById(block_id);
    await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            room_id: room_id,
            date_from: date_from,
            date_to: date_to
        }),
    }).then(response => {
        if (response.status === 201) {
            alert("Номер добавлен в корзину");

            refresh_nav();
        }
        else if (response.status === 401) {
            fetch("/auth/refresh", {method: "POST"})
            .then(response => {
                if (response.status === 200) {
                    fetch(url, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            room_id: room_id,
                            date_from: date_from,
                            date_to: date_to
                        }),
                    }).then(response => {
                        if (response.status === 201) {
                            alert("Номер добавлен в корзину");
                
                            refresh_nav();
                        }})} //this
                        else if (response.status === 401) {

                            //!!!!!!!добавить код для анона
                            fetch("/cart/anon", {
                                method: 'POST',
                                headers: { 'Content-Type': 'application/json' },
                                body: JSON.stringify({
                                    room_id: room_id,
                                    date_from: date_from,
                                    date_to: date_to
                                }),
                            }).then(response => {
                                if (response.status === 201) {
                                    alert("Номер добавлен в корзину");
                                    refresh_anon_nav();
                                }
                                else if (response.status === 422) {
                                    alert("Выберите даты бронирования");
                                }
                                else if (response.status === 401) {
                                    alert("Войдите или зарегистрируйтесь");
                                }
                            });
                        }                   
                    })
                }
                else if (response.status === 422) {
                    alert("Выберите даты бронирования");               
        }
        
        }       
    )};




function sleep (time) {
    return new Promise((resolve) => setTimeout(resolve, time));
  }


//переписан
function book_all_checked() {
    var choice = []
    var choice_list = document.getElementsByClassName('choice');
    for (var i = 0; i < choice_list.length; i++) {
        if (choice_list[i].checked) {
            const strng = choice_list[i].value.split('/');
            strng.push(choice_list[i].name)
            choice.push(strng);
        }
    }
    url = "/bookings";
    for (let i = 0; i < choice.length; i++) {


        fetch(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                room_id: Number(choice[i][0]),
                date_from: choice[i][1],
                date_to: choice[i][2]
            }),
        }).then(response => {
            if (response.status === 401) {
                fetch("/auth/refresh", { method: "POST" })
                    .then(response => {
                        if (response.status === 200) {
                            fetch(url, {
                                method: 'POST',
                                headers: { 'Content-Type': 'application/json' },
                                body: JSON.stringify({
                                    room_id: Number(choice[i][0]),
                                    date_from: choice[i][1],
                                    date_to: choice[i][2]
                                }),
                            }).then(response => {
                                if (response.status != 200) {
                                    alert("Ошибка бронирования");

                                } else {
                                    url_1 = "/cart/" + choice[i][3];
                                    fetch(url_1, { method: 'DELETE' });
                                        

                                    let myDiv = document.getElementById('bookings_list');
                                    fetch('/pages/cart', {headers: { 'myHeader': 'true' }})
                                        .then(response => response.text())
                                        .then(data => { myDiv.innerHTML = data, htmx.process(myDiv); });
                                    refresh_nav();
                                }

                            }
                            )

                        }
                    })
            } else {
                url_1 = "/cart/" + choice[i][3];
                fetch(url_1, { method: 'DELETE' });

                let myDiv = document.getElementById('bookings_list');
                fetch('/pages/cart', {headers: { 'myHeader': 'true' }})
                    .then(response => response.text())
                    .then(data => { myDiv.innerHTML = data, htmx.process(myDiv); });
                refresh_nav();


            }
        });
        sleep(200);


    }
    
}

//переписан
async function add_fav(room_id, hotel_id, block_id) {
    const url = "/fav";
    const date_from = document.getElementById("date_from").value;
    const date_to = document.getElementById("date_to").value;
    let myDiv = document.getElementById('nav_box');
    let myDiv_1 = document.getElementById(block_id);
    await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            id: room_id,
            h_id: hotel_id,
        }),
    }).then(response => {
        if (response.status === 201) {
            var url_1 = '/pages/hotels/' + hotel_id + '/rooms?date_from=' + date_from + '&date_to=' + date_to;
            fetch(url_1, {headers: { 'myHeader': 'true' }})
                .then(response => response.text())
                .then(data => { myDiv_1.innerHTML = data, htmx.process(myDiv_1) });
            refresh_nav();
        }
        else if (response.status === 401) {
            fetch("/auth/refresh", {method: "POST"})
            .then(response => {
                if (response.status === 200) {
                    fetch(url, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            id: room_id,
                            h_id: hotel_id,
                        }),
                    }).then(response => {
                        if (response.status === 201) {
                            var url_1 = '/pages/hotels/' + hotel_id + '/rooms?date_from=' + date_from + '&date_to=' + date_to;
                            fetch(url_1, {headers: { 'myHeader': 'true' }})
                                .then(response => response.text())
                                .then(data => { myDiv_1.innerHTML = data, htmx.process(myDiv_1) });
                            refresh_nav();
                        }
                    })   
                } else if (response.status === 401) {
                    fetch("/fav/anon", {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            id: room_id,
                            h_id: hotel_id,
                        }),
                    }).then(response => {
                        if (response.status === 201) {
                            var url_1 = '/pages/hotels/' + hotel_id + '/rooms?date_from=' + date_from + '&date_to=' + date_to;
                            fetch(url_1, {headers: { 'myHeader': 'true' }})
                                .then(response => response.text())
                                .then(data => { myDiv_1.innerHTML = data, htmx.process(myDiv_1); });
                            refresh_anon_nav();
                        }
                    });
                }
                })    
        } 
        else if (response.status === 409) {
            alert(response.statusText);
        }
    })
}


//переписан
async function add_fav_from_cart(room_id, hotel_id) {
    const url = "/fav";
    let myDiv = document.getElementById('nav_box');
    let myDiv_1 = document.getElementById("bookings_list");
    await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            id: room_id,
            h_id: hotel_id,
        }),
    }).then(response => {
        if (response.status === 201) {
            var url_1 = '/pages/cart';
            fetch(url_1, {headers: { 'myHeader': 'true' }})
                .then(response => response.text())
                .then(data => { myDiv_1.innerHTML = data, htmx.process(myDiv_1) });
            refresh_nav();
        }
        else if (response.status === 401) {
            fetch("/auth/refresh", {method: "POST"})
            .then(response => {
                if (response.status === 200) {
                    fetch(url, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            id: room_id,
                            h_id: hotel_id,
                        }),
                    }).then(response => {
                        if (response.status === 201) {
                            var url_1 = '/pages/cart';
                            fetch(url_1, {headers: { 'myHeader': 'true' }})
                                .then(response => response.text())
                                .then(data => { myDiv_1.innerHTML = data, htmx.process(myDiv_1) });
                            refresh_nav();
                        }})
                } else if (response.status === 401) {
                    
                    fetch("/fav/anon", {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            id: room_id,
                            h_id: hotel_id,
                        }),
                    }).then(response => {
                        if (response.status === 201) {
                            var url_1 = '/pages/hotels/' + hotel_id + '/rooms?date_from=' + date_from + '&date_to=' + date_to;
                            fetch(url_1, {headers: { 'myHeader': 'true' }})
                                .then(response => response.text())
                                .then(data => { myDiv_1.innerHTML = data, htmx.process(myDiv_1); });
                            refresh_anon_nav();
                        }
                    });
                    } 
            })
        } else if (response.status === 409) {
            alert(response.statusText);
        }
    })
}


// переписан
async function add_fav_single(room_id, hotel_id) {
    const url = "/fav";
    let myDiv = document.getElementById(room_id);
    let myDiv_1 = document.getElementById("bookings_list");
    await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            id: room_id,
            h_id: hotel_id,
        }),
    }).then(response => {
        if (response.status === 201) {
            if (myDiv.className === "fi fi-ss-heart") {
                myDiv.className = "fi fi-rs-heart";
            }
            else {
                myDiv.className = "fi fi-ss-heart";
            }
            refresh_nav();
        }
        else if (response.status === 401) {
            fetch("/auth/refresh", {
                method: 'POST',
            })
                .then(response => {
                    if (response.status === 200) {

                        fetch(url, {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({
                                id: room_id,
                                h_id: hotel_id,
                            }),
                        }).then(response => {
                            if (response.status === 201) {
                                if (myDiv.className === "fi fi-ss-heart") {
                                    myDiv.className = "fi fi-rs-heart";
                                }
                                else {
                                    myDiv.className = "fi fi-ss-heart";
                                }
                                refresh_nav();
                            }
                        })
                    }
                    else if (response.status === 401) {
                        fetch("/fav/anon", {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({
                                id: room_id,
                                h_id: hotel_id,
                            }),
                        }).then(response => {
                            if (response.status === 201) {
                                var url_1 = '/pages/hotels/' + hotel_id + '/rooms?date_from=' + date_from + '&date_to=' + date_to;
                                fetch(url_1, {headers: { 'myHeader': 'true' }})
                                    .then(response => response.text())
                                    .then(data => { myDiv_1.innerHTML = data, htmx.process(myDiv_1); });
                                refresh_anon_nav();
                            }
                        });
                        
                    }
                });
        }
        else if (response.status === 409) {
            alert(response.statusText);
        }

    })

}

function setLoc(loc) {
    let myDiv = document.getElementById("loc");
    myDiv.value = loc.replace(/_/gi, " ");
    cancel("loc_list");
}

function showChat() {
    let myDiv = document.getElementById("chat");
    myDiv.style.visibility = "visible";
    
}

function hiddenChat() {
    let myDiv = document.getElementById("chat");
    myDiv.style.visibility = "hidden";
    
}






window.onclick = function (event) {
    if (!event.target.matches('.dropbtn')) {
        cancel("loc_list");
    }

    else {

    }
}
