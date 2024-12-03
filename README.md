# Spotify Playlist Tool

## Project Description
The Spotify Playlist Analytics project is a web application built with Django that integrates with the Spotify API to fetch, analyze, and visualize data about Spotify playlists. It provides users with insights into their top artists, top tracks, and audio features like popularity, danceability, energy, and valence. Users can explore data from different time frames (4 weeks, 6 months, and 1 year) and view detailed visualizations and analysis of their playlists.

## Important Note on Spotify API Changes
During the development of this project, Spotify made significant changes to their [Web API (announced on November 27, 2024)](https://developer.spotify.com/blog/2024-11-27-changes-to-the-web-api), which deprecated several endpoints, including the Audio Features endpoint.  Due to this update, I am currently generating random data for the audio features (such as danceability, energy, tempo, etc.) instead of fetching them from the Spotify API. The project currently uses simulated random data in place of the actual Spotify audio feature data. This does not affect other features of the app, such as playlist display, artist information, or track details.

## Distinctiveness and Complexity
This project satisfies the distinctiveness and complexity requirements in the following ways:

1. **Integration with External API (Spotify)**: 
   - The project uses the Spotify API to fetch data about tracks, artists, and playlists. This integration handles OAuth2 authentication, retrieves data in real-time, and ensures that the app updates database dynamically as new data is fetched.

2. **Data Visualization Using Chart.js**: 
   - One of the key aspects that sets this project apart is the incorporation of Chart.js to visualize detailed analytics of Spotify playlists. The application generates dynamic bar charts to represent the top tracks based on their popularity, danceability, energy, instrumentalness, tempo, and valence scores. These charts are not only interactive but also provide users with an aesthetically appealing and informative experience.

   - The Chart.js library was chosen for its simplicity and flexibility in rendering data visualizations in a web application.

   - The application supports various interactive chart features, such as tooltips showing track names and artists when hovering over data points, and smooth animations when the charts load.

3. **View Your Top 50 Artists**: 
   - User-interactive interface for viewing the top 50 personal artists based on different time ranges. The app dynamically updates the displayed artists by fetching data from the backend when users click on the respective time range buttons.

   - Different time periods (e.g., top artists from the last 4 weeks, 6 months, or past year).

   - The top artists are displayed in a responsive table that shows essential information such as the rank in user's top 50, the artist’s name, followers count, general popularity score, and genres.

   - The JavaScript handles the time button clicks, updates the UI dynamically, and fetches artist data without requiring a page reload, enhancing the overall user experience.

4. **View Your Top 50 Tracks**: 
   - Similar to the Top 50 Artists feature, this section allows users to view their top 50 tracks from different time ranges.

   - The app displays essential details for each track, including rank, track name, artist(s), album, and popularity score.

5. **Direct Links to Spotify Content**: 
   - The app provides direct Spotify links for albums, artists and tracks, allowing users to easily access the original content on the Spotify platform. By clicking on an artist's name, track title, or album, users are seamlessly redirected to the corresponding Spotify page for further exploration and interaction.

6. **Pagination**: 
   - Tracks on the statistics page are paginated for a cleaner user experience and improved performance. 

7. **Responsive Design**:
   - The project is designed with responsiveness in mind, ensuring that the application works seamlessly across different devices, including desktops, tablets, and mobile phones. Bootstrap is used to make the frontend look professional and adaptable to various screen sizes.

## Files
### `static/playlist_tool/`
- **`topArtists.js`**: JavaScript file that handles dynamic updates for viewing the top 50 artists. It fetches data from the backend based on the selected time range (e.g., last 4 weeks, 6 months, past year) and updates the user interface accordingly.
- **`topTracks.js`**: JavaScript file that manages the top 50 tracks feature. Similar to `topArtists.js`, it dynamically loads track data from the backend based on the selected time range and updates the display without a page reload.

### `templates/playlist_tool/`
- **`layout.html`**: The base template that includes common elements such as the header, footer, and navigation. Other templates extend this base layout to maintain a consistent look across all pages.
- **`index.html`**: The main landing page of the application that introduces the user to the various features and provides navigation to other pages like profile, top artists, and top tracks.
- **`profile.html`**: Displays user-specific information such as username, profile picture, followers, email, and user's playlists.
- **`statistics.html`**: Shows detailed analytics and statistics table for playlist, including the track rank, artists, popularity, and audio features.
- **`top_artists.html`**: Displays a table of the user's top 50 artists, allowing users to filter by time range (e.g., last 4 weeks, 6 months, past year). It dynamically updates based on user selection.
- **`top_tracks.html`**: Similar to `top_artists.html`, this page shows the user's top 50 tracks.
- **`visualize_data.html`**: The page where data visualizations such as bar charts are shown for track characteristics like popularity, danceability, energy, tempo and valence powered by **Chart.js**.

### `urls.py`
Defines the URL routing for the application, mapping user requests to the appropriate views for pages like top artists, top tracks, and statistics.

### `views.py`
Contains the logic for handling requests and rendering the corresponding templates, including fetching data from the backend and passing it to the templates.

### `models.py`
Defines the database models used to store user and playlist data, including models for top tracks, artists, and related user information.

### `admin.py`
Registers the application's models with the Django admin interface to enable easy management of data like top tracks, artists, and user details.

## Installation
1. **Clone the Repository**:
```bash
git clone https://github.com/aegis945/spotify_project
cd spotify_project
```
2. **Create a Virtual Environment**
```bash
python -m venv venv
```
3. **Activate the Virtual Environment**:
   
  - On macOS/Linux:
```bash
source venv/bin/activate
```
  - On Windows: 
```bash
venv\Scripts\activate
```
4. **Install dependencies**:
```bash
pip install -r requirements.txt
```
5. **Set Up Spotify Developer App**
- You must have a Spotify Premium account to run this project.
- [Go to the Spotify Develop Dashboard](https://developer.spotify.com/) and log in with your Spotify account
- Click "Create app"
- Fill in the App name and App description.
- For the Redirect URI, use:
```bash
http://127.0.0.1:8000/callback
```
- Select Web API, agree with terms and click save.
- After creating the app, note down the Client ID and Client Secret for later use.

6. **Set Up Environment Variables: Create a .env file in the project root directory and define your environment variables.** If you don't have a django secret key, it will be generated by function get_random_secret_key():
```bash
SECRET_KEY=your_secret_key
DEBUG=False
SPOTIPY_CLIENT_ID=your_spotify_client_id
SPOTIPY_CLIENT_SECRET=your_spotify_client_secret
SPOTIFY_REDIRECT_URI=http://127.0.0.1:8000/callback
```
7. **Make migrations and migrate the database**
```bash
python manage.py makemigrations
python manage.py migrate
```
8. **Run dev server**:
```bash
python manage.py runserver
```
9. **Open your web browser and go to http://127.0.0.1:8000**
