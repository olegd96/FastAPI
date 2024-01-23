async function refresh_nav(){
    let myDiv = document.getElementById('nav_box');
    fetch('pages/bookings')
        .then(response => response.text())
        .then(data => { myDiv.innerHTML = data, htmx.process(myDiv); } );
}