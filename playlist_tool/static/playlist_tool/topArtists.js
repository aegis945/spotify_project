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

    fetch(`/fetch_top_artists/?time_range=${encodeURIComponent(timeRange)}&limit=50`)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP ${response.status} - ${response.statusText}`);
            }
            return response.json();
        })
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
    container.innerHTML = "";

    const table = document.createElement("table");
    table.classList.add("table", "table-striped", "align-middle");

    const thead = document.createElement("thead");
    thead.innerHTML = `
        <tr>
            <th scope="col" class="text-center">Rank</th>
            <th scope="col">Artist</th>
            <th scope="col">Followers</th>
            <th scope="col">Popularity<br>(0-100)</th>
            <th scope="col">Genres</th>
        </tr>
    `;
    table.appendChild(thead);

    const tbody = document.createElement("tbody");

    artists.forEach((artist, index) => {
        const row = document.createElement("tr");

        const rankCell = document.createElement("td");
        rankCell.classList.add("text-center");
        rankCell.textContent = index + 1;
        row.appendChild(rankCell);

        const artistCell = document.createElement("td");
        const artistLink = document.createElement("a");
        artistLink.href = artist.external_urls?.spotify || "#";
        artistLink.target = "_blank";
        artistLink.classList.add("link-primary");
        artistLink.textContent = artist.name || "Unknown Artist";

        if (artist.images?.[0]?.url) {
            const artistImage = document.createElement("img");
            artistImage.src = artist.images[0].url;
            artistImage.alt = artist.name || "No Image Available";
            artistImage.style = "width: 40px; height: 40px; margin-right: 8px; border-radius: 50%;";
            artistCell.appendChild(artistImage);
        }
        artistCell.appendChild(artistLink);
        row.appendChild(artistCell);

        const followersCell = document.createElement("td");
        followersCell.textContent = artist.followers?.total?.toLocaleString() || "N/A";
        row.appendChild(followersCell);

        const popularityCell = document.createElement("td");
        popularityCell.textContent = artist.popularity ?? "N/A";
        row.appendChild(popularityCell);

        const genresCell = document.createElement("td");
        genresCell.textContent = (artist.genres || []).map((genre) =>
            genre
                .split(" ")
                .map((word) => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
                .join(" ")
        ).join(", ") || "N/A";
        row.appendChild(genresCell);

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
    heading.textContent = timeRangeMapping[timeRange] || "Top 50 Artists";
}
