
async function logoutUser() {
    const url = "http://localhost:8000/auth/logout";

    await fetch(url, {
        method: 'POST',
    }).then(response => {
        if (response.status === 200) {
            window.location.href = "/pages"
        }
    });
}
