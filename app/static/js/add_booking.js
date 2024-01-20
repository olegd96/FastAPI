async function add_booking() {
    
   
    
    const url = "http:./bookings";
    const room_id = document.getElementById("room_id").value;
    const date_from = document.getElementById("date_from").value;
    const date_to = document.getElementById("date_to").value;
    await fetch(url, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'}, 
        body: JSON.stringify({room_id: room_id, 
                            date_from: date_from,
                            date_to: date_to}),
        }).then(response => {
        if (response.status === 200) {
            alert("Номер добавлен в корзину");
        }
        else if (response.status === 401) {
            alert("Войдите в систему");
        }
        else if (response.status === 409) {
            alert("Не осталось свободных номеров");
        }
        
});
}