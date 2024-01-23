
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
