      
        



async function add_booking(room_id, hotel_id, block_id) {
    const url = "/bookings";
    const date_from = document.getElementById("date_from").value;
    const date_to = document.getElementById("date_to").value;
    let myDiv = document.getElementById('nav_box');
    let myDiv_1 = document.getElementById(block_id);
    await fetch(url, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'}, 
        body: JSON.stringify({room_id: room_id, 
                            date_from: date_from,
                            date_to: date_to}),
        }).then(response => {
        if (response.status === 200) {
            
            alert("Номер добавлен в корзину");
            
            
            var url_1 = 'pages/hotels/' + hotel_id + '/rooms?date_from=' + date_from + '&date_to=' + date_to;
            fetch('pages/bookings')
                .then(response => response.text())
                .then(data => { myDiv.innerHTML = data, htmx.process(myDiv); } );
            fetch(url_1)
                .then(response => response.text())
                .then(data => { myDiv_1.innerHTML = data, htmx.process(myDiv_1); } );
            
        }
        else if (response.status === 401) {
            alert("Войдите в систему");
        }
        else if (response.status === 409) {
            alert("Не осталось свободных номеров");
        }
        
});
}