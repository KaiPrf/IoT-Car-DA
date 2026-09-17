async function loadInfo() {
    try {
        const response =
            await fetch(
                "/api/info",
                {
                    cache: "no-store"
                }
            );

        const data =
            await response.json();

        document.getElementById(
            "port"
        ).textContent =
            data.port;

        document.getElementById(
            "network-name"
        ).textContent =
            data.network_name;

        document.getElementById(
            "host-ip"
        ).textContent =
            data.public_host;

        document.getElementById(
            "control-url"
        ).textContent =
            data.control_url;

        document.getElementById(
            "control-qr"
        ).src =
            `/api/qr.png?t=${Date.now()}`;

    } catch (error) {
        document.getElementById(
            "control-url"
        ).textContent =
            "Informationen konnten nicht geladen werden.";
    }
}

loadInfo();
