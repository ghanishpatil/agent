document.addEventListener("DOMContentLoaded", function () {

    fetch("/static/report.pdf");

    const h = window.location.hash.replace("#", "");

    const btn = document.getElementById("notesBtn");
    const msg = document.getElementById("message");
    const msg1 = document.getElementById("message1");

    // ALWAYS hide first
    btn.style.display = "none";

    if (h === "draft") {

        const encoded = "U29tZSByZWNvcmRzIG1heSBwZXJzaXN0IGJleW9uZCBleHBlY3RlZCBsaWZlY3ljbGUu";
        msg.innerText = atob(encoded);
        msg.style.display = "block";

        msg1.innerHTML = `
            <p>Draft environment loaded.</p>
            <p>Access endpoint: /api/notes?token=draftkey123</p>
        `;
        msg1.style.display = "block";

        btn.style.display = "inline-block";
    }

});