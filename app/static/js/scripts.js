"use strict";
// document.addEventListener("htmx:confirm", function(e) {
//     e.preventDefault()
//     showMdAlrt(`${e.detail.question}`)
//   })

document.addEventListener('htmx:responseError', function(event){
    if (event.detail.xhr.status === 401){
        fetch("/auth/refresh", {method: "POST"})
        .then (response => {
            if (response.status === 200) {
                const eventType = event.detail.requestConfig.triggeringEvent.type;
                setTimeout(function(){
                htmx.trigger(event.detail.elt, eventType)
                }, 1000);
            } 
            else {
                // dialog.style.display = "block";
                // message.textContent = "Войдите в систему";
                // dialog.showModal();
                showPopUp("Войдите в систему");
            }
        } 
        )            
    } else if (event.detail.xhr.status === 422) {
            // dialog.style.display = "block";
            //     message.textContent = "Проверьте корректность данных";
            //     dialog.showModal();
            showPopUp("Проверьте корректность данных");
    }
    else {
        let res = JSON.parse(event.detail.xhr.responseText)
        // dialog.style.display = "block";
        // message.textContent = res.detail;
        // dialog.showModal();
        showPopUp(res.detail);
    }

})



document.addEventListener('htmx:configRequest', function(event) {
    event.detail.headers['myHeader'] = 'true'
}
)

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

            const url_1 = '/pages/hotels/' + hotel_id + '/rooms?date_from=' + date_from + '&date_to=' + date_to;
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

                    const url_1 = '/pages/hotels/' + hotel_id + '/rooms?date_from=' + date_from + '&date_to=' + date_to;
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
    if (obj) {
    obj.style.display = "none"};
}


function verify_password() {
    let password = document.getElementById("new_pass")
    let re_password = document.getElementById("new_pass_re")
    let done = document.getElementById("done")
    if (password.value != re_password.value) {
        re_password.style.background = "#FFE3E3";
        done.style.visibility = "hidden";
    } else {
        re_password.style.background = "#EFFCF6";
        password.style.background = "#EFFCF6";
        done.style.visibility = "visible";
    }
}

function view_message() {
    let stat = document.getElementById("status")
    let message = JSON.parse(stat.textContent)
    stat.textContent = message["message"]
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
    }).then(response => response.json())
    .then(res => {
        if ("access_token" in res) {
            const url = "/pages/bookings";
            fetch(url, {headers: { 'myHeader': 'true' }})
                .then(response => response.text())
                .then(data => { myDiv.innerHTML = data, htmx.process(myDiv);booking_menu_scr(); });
            cancel("logpanel");
            refresh_panel();
        } 
        else {
            wrongCredentialsSpan.textContent = res.detail;
        }
    });
}

async function logoutUser() {
    const url = "/auth/logout";

    await fetch(url, {
        method: 'POST',
    }).then(response => {
        if (response.status === 200) {
            window.location.href = "/pages";
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
                wrongCredentialsSpan.textContent = "Вы зарегистрированы. Подтвердите email.";
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
    await fetch('/pages/bookings', {headers: { 'myHeader': 'true' }})
        .then(response => {
            if (response.status === 200) {            
                (response.text())
                .then(data => { myDiv.innerHTML = data, htmx.process(myDiv); booking_menu_scr();});}
                
            else {
                fetch('/auth/refresh', {method: 'POST'})
                .then(response => {
                    if (response.status === 200) {
                        fetch('/pages/bookings', {headers: { 'myHeader': 'true' }})
                        .then(response => {
                            if (response.status === 200) {            
                                (response.text())
                                .then(data => { myDiv.innerHTML = data, htmx.process(myDiv);booking_menu_scr(); });}                   
                })
            }})
}
})
}


async function refresh_anon_nav() {
    let myDiv = document.getElementById('nav_box');
    await fetch('/pages/anon_bookings', {headers: { 'myHeader': 'true' }})
        .then(response => {
            if (response.status === 200) {
            (response.text())
            .then(data => { myDiv.innerHTML = data, htmx.process(myDiv); booking_menu_scr();});
        }   
    })
}


async function refresh_account() {
    let myDiv = document.getElementById('bookings_list');
    await fetch('/pages/personal_account', {headers: { 'myHeader': 'true' }})
        .then(response => response.text())
        .then(data => { myDiv.innerHTML = data, htmx.process(myDiv); });
}

//переписано
async function refresh_my_bookings() {
    let myDiv = document.getElementById('bookings_list');
    await fetch('/pages/my_bookings', {headers: { 'myHeader': 'true' }})
    .then(response => {
        if (response.status === 200) {            
    (response.text())
    .then(data => { myDiv.innerHTML = data, htmx.process(myDiv); });}
})
}

//переписано
async function refresh_my_cart() {
    let myDiv = document.getElementById('bookings_list');
    await fetch('/pages/cart', {headers: { 'myHeader': 'true' }})
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
        await fetch('/pages/cart', {headers: { 'myHeader': 'true' }})
            .then(response => response.text())
            .then(data => { myDiv_1.innerHTML = data, htmx.process(myDiv_1); });
    }
}

async function refresh_anon_cart() {
    let myDiv = document.getElementById('bookings_list');
    await fetch('/pages/cart/anon', {headers: { 'myHeader': 'true' }})
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
            // alert("Номер добавлен в корзину");
            showPopUp("Номер добавлен в корзину");
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
                            // alert("Номер добавлен в корзину");
                            showPopUp("Номер добавлен в корзину");
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
                                    // alert("Номер добавлен в корзину");
                                    showPopUp("Номер добавлен в корзину");
                                    refresh_anon_nav();
                                }
                                else if (response.status === 422) {
                                    // alert("Выберите даты бронирования");
                                    showPopUp("Выберите даты бронирования");
                                }
                                else if (response.status === 401) {
                                    // alert("Войдите или зарегистрируйтесь");
                                    showPopUp("Войдите или зарегистрируйтесь");
                                }
                            });
                        }                   
                    })
                }
                else if (response.status === 422) {
                    // alert("Выберите даты бронирования");
                    showPopUp("Выберите даты бронирования");              
        }
        
        }       
    )};




function sleep (time) {
    return new Promise((resolve) => setTimeout(resolve, time));
  }


//переписан
async function book_all_checked() {
    let choice = []
    let choice_list = document.getElementsByClassName('choice');
    for (let i = 0; i < choice_list.length; i++) {
        if (choice_list[i].checked) {
            const strng = choice_list[i].value.split('/');
            strng.push(choice_list[i].name)
            choice.push(strng);
        }
    }
    let url = "/bookings";
    for (let i = 0; i < choice.length; i++) {


        await fetch(url, {
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
                                    // alert("Ошибка бронирования");
                                    showPopUp("Ошибка бронирования");

                                } else {
                                    const url_1 = "/cart/" + choice[i][3];
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
                const url_1 = "/cart/" + choice[i][3];
                fetch(url_1, { method: 'DELETE' })
                .then(response => {
                    if (response.status === 200) {
                let myDiv = document.getElementById('bookings_list');
                fetch('/pages/cart', {headers: { 'myHeader': 'true' }})
                    .then(response => response.text())
                    .then(data => { myDiv.innerHTML = data, htmx.process(myDiv); });
                refresh_nav();}
            })

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
            const url_1 = '/pages/hotels/' + hotel_id + '/rooms?date_from=' + date_from + '&date_to=' + date_to;
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
                            const url_1 = '/pages/hotels/' + hotel_id + '/rooms?date_from=' + date_from + '&date_to=' + date_to;
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
                            const url_1 = '/pages/hotels/' + hotel_id + '/rooms?date_from=' + date_from + '&date_to=' + date_to;
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
            // alert(response.statusText);
            showPopUp(response.statusText);
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
            const url_1 = '/pages/cart';
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
                            const url_1 = '/pages/cart';
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
                            const url_1 = '/pages/hotels/' + hotel_id + '/rooms?date_from=' + date_from + '&date_to=' + date_to;
                            fetch(url_1, {headers: { 'myHeader': 'true' }})
                                .then(response => response.text())
                                .then(data => { myDiv_1.innerHTML = data, htmx.process(myDiv_1); });
                            refresh_anon_nav();
                        }
                    });
                    } 
            })
        } else if (response.status === 409) {
            // alert(response.statusText);
            showPopUp(response.statusText);
        }
    })
}


// переписан
async function add_fav_single(room_id, hotel_id) {
    const url = "/fav";
    let myDivs = [];
    myDivs = document.querySelectorAll(`[id="${room_id}"]`);
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
            for (let i = 0; i<myDivs.length; i++){
            if (myDivs[i].className === "fi fi-ss-heart") {
                myDivs[i].className = "fi fi-rs-heart";
            }
            else {
                myDivs[i].className = "fi fi-ss-heart";
            }}
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
                                for (let i = 0; i<myDivs.length; i++){
                                    if (myDivs[i].className === "fi fi-ss-heart") {
                                        myDivs[i].className = "fi fi-rs-heart";
                                    }
                                    else {
                                        myDivs[i].className = "fi fi-ss-heart";
                                    }}
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
                                for (let i = 0; i<myDivs.length; i++){
                                    if (myDivs[i].className === "fi fi-ss-heart") {
                                        myDivs[i].className = "fi fi-rs-heart";
                                    }
                                    else {
                                        myDivs[i].className = "fi fi-ss-heart";
                                    }}
                                refresh_anon_nav();
                            }
                        });
                        
                    }
                });
        }
        else if (response.status === 409) {
            // alert(response.statusText);
            showPopUp(response.statusText);
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
   
    toggleTwoClasses(myDiv, "is-visible", "is-hidden", 300);
    myDiv.style.visibility = "visible";
}

function hiddenChat() {
    let myDiv = document.getElementById("chat");
    
    toggleTwoClasses(myDiv, "is-visible", "is-hidden", 300);
    window.setTimeout(function() {
        myDiv.style.visibility = "hidden";
        }, 200);
    
}

// function toggleTwoClasses(element, first, second, timeOfAnimation) {
//     if (!element.classList.contains(first)) {
//         element.classList.add(first);
//         element.classList.remove(second);
//     } else {
//         element.classList.add(second);
//         window.setTimeout(function() {
//         element.classList.remove(first);
//         element.style.display = "";
//         }, timeOfAnimation);
//     }
//     }

function toggleTwoClasses(element, first, second, timeOfAnimation) {
    if (!element.classList.contains(first)) {
        element.classList.add(first);
        element.classList.remove(second);

    } else {
        element.classList.add(second);
        window.setTimeout(function() {
        element.classList.remove(first);
        element.style.display = "";
        }, timeOfAnimation);
    }
    }


window.onclick = function (event) {
    if (!event.target.matches('.dropbtn')) {
        cancel("loc_list");
    }

    else {

    }
}

function booking_menu_scr() {
    let brgr = document.querySelector('.burger');
    let wrapper = document.querySelector('.wrapper');
    let nav_lab = document.getElementsByClassName('nav_lab');
    brgr.addEventListener('click', () => {
        wrapper.classList.toggle('wrapper_show');
        brgr.classList.toggle('burger-close');
    })

    for (let i = 0; i < nav_lab.length; i++) {


        nav_lab[i].addEventListener('click', () => {
            brgr.classList.toggle('burger-close');
            wrapper.classList.toggle('wrapper_show');
        })
    };
}




