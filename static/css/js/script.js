function parseDeadline(dateText) {
    if (!dateText) {
        return null;
    }

    dateText = dateText.trim();

    const months = {
        january: 0,
        february: 1,
        march: 2,
        april: 3,
        may: 4,
        june: 5,
        july: 6,
        august: 7,
        september: 8,
        october: 9,
        november: 10,
        december: 11
    };

    // Format: 29 September 2026
    const match = dateText.match(
        /^(\d{1,2})\s+([A-Za-z]+)\s+(\d{4})$/
    );

    if (match) {
        const day = parseInt(match[1]);
        const monthName = match[2].toLowerCase();
        const year = parseInt(match[3]);

        if (months[monthName] !== undefined) {
            return new Date(
                year,
                months[monthName],
                day,
                23,
                59,
                59
            );
        }
    }

    return null;
}


function updateCountdowns() {

    const countdowns = document.querySelectorAll(".countdown");

    countdowns.forEach(function(element) {

        const deadlineText = element.dataset.deadline;

        if (!deadlineText) {
            element.innerHTML = "⚠️ Deadline unavailable";
            return;
        }

        const deadline = parseDeadline(deadlineText);

        if (!deadline) {
            element.innerHTML = "⚠️ Countdown unavailable";
            return;
        }

        const now = new Date();

        const difference =
            deadline.getTime() - now.getTime();

        if (difference <= 0) {

            element.innerHTML =
                "🔴 Registration Closed";

            element.classList.add("closed");

            return;
        }

        const totalSeconds =
            Math.floor(difference / 1000);

        const days =
            Math.floor(totalSeconds / 86400);

        const hours =
            Math.floor(
                (totalSeconds % 86400) / 3600
            );

        const minutes =
            Math.floor(
                (totalSeconds % 3600) / 60
            );

        const seconds =
            totalSeconds % 60;


        if (days > 0) {

            element.innerHTML =
                "🔥 " +
                days +
                " days " +
                hours +
                " hours left";

        } else {

            element.innerHTML =
                "⚡ " +
                hours +
                "h " +
                minutes +
                "m " +
                seconds +
                "s left";
        }

    });
}


// Run immediately
updateCountdowns();


// Update every second
setInterval(updateCountdowns, 1000);