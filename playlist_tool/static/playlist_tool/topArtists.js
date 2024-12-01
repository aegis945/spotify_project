document.addEventListener("DOMContentLoaded", () => {
    handleTimeButtonClicks();
    loadTopArtists('short_term');
    setActiveButton(document.querySelector('#short_term'));
});

function handleTimeButtonClicks() {
    const timeButtons = document.querySelectorAll(".btn-group button");

    const timeRangeMapping = {
        short_term: "Top Artists from the last 4 weeks",
        medium_term: "Top Artists from the last 6 months",
        long_term: "Top Artists from the past year"
    };

    timeButtons.forEach(button => {
        button.addEventListener("click", () => {
            const timeRange = button.id;
            if (button.classList.contains("active")) {
                return;
            }
            loadTopArtists(timeRange);
            setActiveButton(button);
            updateHeading(timeRange, timeRangeMapping);
        });
    });
}

function loadTopArtists(timeRange) {
    const container = document.querySelector("#artists-container");

    container.innerHTML = `<div class="spinner-border" role="status">
                            <span class="visually-hidden">Loading...</span>
                          </div>`;

    fetch(`/fetch_top_artists/?time_range=${timeRange}&limit=50`)
        .then(response => response.json())
        .then(data => {
            if (data.items) {
                displayArtists(data.items);
            } else {
                container.innerHTML = "<p>No artists found.</p>";
            }
        })
        .catch(error => {
            container.innerHTML = "<p>Error loading artists.</p>";
            console.error("Error loading artists:", error);
        });
}

function displayArtists(artists) {
    const container = document.querySelector("#artists-container");
    let html = `
        <table class="table table-striped align-middle">
            <thead>
                <tr>
                    <th class="text-center">Rank</th>
                    <th>Artist</th>
                    <th>Followers</th>
                    <th>Popularity<br>(0-100)</th>
                    <th>Genres</th>
                </tr>
            </thead>
            <tbody>
    `;

    artists.forEach((artist, index) => {
        html += `
            <tr>
                <td class="text-center">${index + 1}</td>
                <td>
                    <a class="link-primary link-offset-2 link-underline-opacity-25 link-underline-opacity-100-hover" href="${artist.external_urls.spotify}" target="_blank"><img src="${artist.images[0].url}" alt="${artist.name} Image" style="width: 40px; height: 40px; margin-right: 8px; border-radius: 50%;">
                    ${artist.name}</a>
                </td>
                <td>${artist.followers.total}</td>
                <td>${artist.popularity}</td>
                <td>${artist.genres.map(genre => genre.split(" ").map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase()).join(" ")).join(", ")}</td>
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
    heading.textContent = timeRangeMapping[timeRange] || "Top 50 Artists";
}
