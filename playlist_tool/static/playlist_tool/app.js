document.addEventListener("DOMContentLoaded", () => {
    handleTimeButtonClicks();
    loadTopTracks('short_term');
    setActiveButton(document.querySelector('#short_term'));
});

function handleTimeButtonClicks() {
    const timeButtons = document.querySelectorAll(".btn-group button");

    const timeRangeMapping = {
        short_term: "Top 50 Tracks from the last 4 weeks",
        medium_term: "Top 50 Tracks from the last 6 months",
        long_term: "Top 50 Tracks from the past year"
    };

    timeButtons.forEach(button => {
        button.addEventListener("click", () => {
            const timeRange = button.id;
            if (button.classList.contains("active")) {
                return;
            }
            loadTopTracks(timeRange);
            setActiveButton(button);
            updateHeading(timeRange, timeRangeMapping);
        });
    });
}

function loadTopTracks(timeRange) {
    const container = document.querySelector("#tracks-container");

    container.innerHTML = `<div class="spinner-border" role="status">
                            <span class="visually-hidden">Loading...</span>
                          </div>`;

    fetch(`/fetch-top-tracks/?time_range=${timeRange}&limit=50`)
        .then(response => response.json())
        .then(data => {
            if (data.items) {
                displayTracks(data.items);
            } else {
                container.innerHTML = "<p>No tracks found.</p>";
            }
        })
        .catch(error => {
            container.innerHTML = "<p>Error loading tracks.</p>";
            console.error("Error loading tracks:", error);
        });
}

function displayTracks(tracks) {
    const container = document.querySelector("#tracks-container");
    let html = `
        <table class="table table-striped">
            <thead>
                <tr>
                    <th>Rank</th>
                    <th>Track</th>
                    <th>Artist</th>
                    <th>Album</th>
                </tr>
            </thead>
            <tbody>
    `;

    tracks.forEach((track, index) => {
        html += `
            <tr>
                <td>${index + 1}</td>
                <td>${track.name}</td>
                <td>${track.artists.map(artist => artist.name).join(", ")}</td>
                <td>${track.album.name}</td>
            </tr>
        `;
    });

    html += "</tbody></table>";
    container.innerHTML = html;
}

function setActiveButton(activeButton) {
    const timeButtons = document.querySelectorAll(".btn-group button");
    timeButtons.forEach(button => {
        button.classList.remove("active");
    });
    activeButton.classList.add("active");
}

function updateHeading(timeRange, timeRangeMapping) {
    const heading = document.querySelector("#top-heading");
    heading.textContent = timeRangeMapping[timeRange] || "Top 50 Tracks";
}
