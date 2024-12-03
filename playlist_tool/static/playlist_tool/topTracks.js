document.addEventListener("DOMContentLoaded", () => {
    handleTimeButtonClicks();
    loadTopTracks('short_term');
    setActiveButton(document.querySelector('#short_term'));
});

function handleTimeButtonClicks() {
    const timeButtons = document.querySelectorAll(".btn-group button");

    const timeRangeMapping = {
        short_term: "Top Tracks from the last 4 weeks",
        medium_term: "Top Tracks from the last 6 months",
        long_term: "Top Tracks from the past year"
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

    fetch(`/fetch_top_tracks/?time_range=${timeRange}&limit=50`)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP ${response.status} - ${response.statusText}`);
            }
            return response.json();
        })
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
    container.innerHTML = "";

    const table = document.createElement("table");
    table.classList.add("table", "table-striped", "align-middle");

    const thead = document.createElement("thead");
    thead.innerHTML = `
        <tr>
            <th scope="col" class="text-center">Rank</th>
            <th scope="col">Track</th>
            <th scope="col">Artist</th>
            <th scope="col">Album</th>
            <th scope="col" class="text-center">Popularity<br>(0-100)</th>
        </tr>
    `;
    table.appendChild(thead);

    const tbody = document.createElement("tbody");

    tracks.forEach((track, index) => {
        const row = document.createElement("tr");

        const rankCell = document.createElement("td");
        rankCell.classList.add("text-center");
        rankCell.textContent = index + 1;
        row.appendChild(rankCell);

        const trackCell = document.createElement("td");
        const trackLink = document.createElement("a");
        trackLink.href = track.external_urls.spotify || "#";
        trackLink.target = "_blank";
        trackLink.classList.add("link-primary");
        trackLink.textContent = track.name || "Unknown Track";

        if (track.album?.images?.[0]?.url) {
            const trackImage = document.createElement("img");
            trackImage.src = track.album.images[0].url;
            trackImage.alt = track.album.name || "No Image Available";
            trackImage.style = "width: 40px; height: 40px; margin-right: 8px; border-radius: 50%;";
            trackCell.appendChild(trackImage);
        }
        trackCell.appendChild(trackLink);
        row.appendChild(trackCell);

        const artistCell = document.createElement("td");
        artistCell.innerHTML = track.artists.map(artist => {
            const artistLink = document.createElement("a");
            artistLink.href = artist.external_urls.spotify || "#";
            artistLink.target = "_blank";
            artistLink.classList.add("link-primary");
            artistLink.textContent = artist.name || "Unknown Artist";
            return artistLink.outerHTML;
        }).join(", ");
        row.appendChild(artistCell);

        const albumCell = document.createElement("td");
        const albumLink = document.createElement("a");
        albumLink.href = track.album.external_urls.spotify || "#";
        albumLink.target = "_blank";
        albumLink.classList.add("link-primary");
        albumLink.textContent = track.album.name || "Unknown Album";
        albumCell.appendChild(albumLink);
        row.appendChild(albumCell);

        const popularityCell = document.createElement("td");
        popularityCell.classList.add("text-center");
        popularityCell.textContent = track.popularity || "N/A";
        row.appendChild(popularityCell);

        tbody.appendChild(row);
    });

    table.appendChild(tbody);
    container.appendChild(table);
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
    heading.textContent = timeRangeMapping[timeRange] || "Top Tracks";
}
