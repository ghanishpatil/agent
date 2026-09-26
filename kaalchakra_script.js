document.addEventListener("DOMContentLoaded", function () {

    const btn = document.getElementById("analyzeBtn");
    const fileInput = document.getElementById("puppyImage");
    const statusBox = document.getElementById("hashStatus");
    const spinner = document.getElementById("loadingSpinner1");
    const clock = document.getElementById("liveTime");

    function updateClock() {
        const now = new Date();

        const timeString = now.toLocaleString("en-US", {
            weekday: "short",
            year: "numeric",
            month: "short",
            day: "numeric",
            hour: "2-digit",
            minute: "2-digit",
            second: "2-digit",
            hour12: true
        });

        clock.textContent = timeString;
    }

    updateClock();
    setInterval(updateClock, 1000);

    btn.addEventListener("click", async function () {

        const file = fileInput.files[0];

        if (!file) {
            showMessage("Please select a file.", "error");
            return;
        }

        btn.disabled = true;
        btn.querySelector("span").textContent = "Processing...";
        spinner.classList.add("show");

        try {

            const data = new FormData();
            data.append("image", file);

            const res = await fetch("/collision", {
                method: "POST",
                body: data
            });

            const result = await res.text();

            showMessage(result, "info");

        } catch (e) {

            showMessage("Request failed ❌", "error");

        } finally {

            btn.disabled = false;
            btn.querySelector("span").textContent = "Analyze Hash";
            spinner.classList.remove("show");

        }

    });

    function showMessage(text, type) {
        statusBox.textContent = text;
        statusBox.className = `status-message ${type} show`;
    }

    fileInput.addEventListener("change", function () {

        const label = this.parentElement.querySelector("label");

        if (this.files.length > 0) {
            label.textContent = this.files[0].name;
        }

    });

});