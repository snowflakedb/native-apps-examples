USE ROLE ACCOUNTADMIN;
CREATE DATABASE IF NOT EXISTS ;
CREATE SCHEMA IF NOT EXISTS SPOTIFY_CORTEX_DB.SPOTIFY_CORTEX_SCHEMA;
CREATE OR REPLACE TABLE SPOTIFY_CORTEX_DB.SPOTIFY_CORTEX_SCHEMA.SPOTIFY_PROVIDER_DATA(
    name VARCHAR,
    artists VARCHAR,
    danceabilty FLOAT
);
INSERT INTO SPOTIFY_CORTEX_DB.SPOTIFY_CORTEX_SCHEMA.SPOTIFY_PROVIDER_DATA VALUES
('God\'s Plan','Drake',0.754),
('SAD!','XXXTENTACION',0.74),
('rockstar (feat. 21 Savage)','Post Malone',0.587),
('Psycho (feat. Ty Dolla Sign)','Post Malone',0.739),
('In My Feelings','Drake',0.835),
('Better Now','Post Malone',0.68),
('I Like It','Cardi B',0.816),
('One Kiss (with Dua Lipa)','Calvin Harris',0.791),
('IDGAF','Dua Lipa',0.836),
('FRIENDS','Marshmello',0.626),
('Havana','Camila Cabello',0.765),
('Lucid Dreams','Juice WRLD',0.511),
('Nice For What','Drake',0.586),
('Girls Like You (feat. Cardi B)','Maroon 5',0.851),
('The Middle','Zedd',0.753),
('All The Stars (with SZA)','Kendrick Lamar',0.698),
('no tears left to cry','Ariana Grande',0.699),
('X','Nicky Jam',0.595),
('Moonlight','XXXTENTACION',0.921),
('Look Alive (feat. Drake)','BlocBoy JB',0.922),
('These Days (feat. Jess Glynne, Macklemore & Dan Caplen)','Rudimental',0.653),
('Te Bot? - Remix','Nio Garcia',0.903),
('Mine','Bazzi',0.71),
('Youngblood','5 Seconds of Summer',0.596),
('New Rules','Dua Lipa',0.762),
('Shape of You','Ed Sheeran',0.825),
('Love Lies (with Normani)','Khalid',0.708),
('Meant to Be (feat. Florida Georgia Line)','Bebe Rexha',0.642),
('Jocelyn Flores','XXXTENTACION',0.872),
('Perfect','Ed Sheeran',0.599),
('Taste (feat. Offset)','Tyga',0.884),
('Solo (feat. Demi Lovato)','Clean Bandit',0.737),
('I Fall Apart','Post Malone',0.556),
('Nevermind','Dennis Lloyd',0.592),
('chame La Culpa','Luis Fonsi',0.726),
('Eastside (with Halsey & Khalid)','benny blanco',0.56),
('Never Be the Same','Camila Cabello',0.637),
('Wolves','Selena Gomez',0.72),
('changes','XXXTENTACION',0.669),
('In My Mind','Dynoro',0.694),
('River (feat. Ed Sheeran)','Eminem',0.748),
('Dura','Daddy Yankee',0.791),
('SICKO MODE','Travis Scott',0.834),
('Thunder','Imagine Dragons',0.605),
('Me Niego','Reik',0.777),
('Jackie Chan','Tiesto',0.747),
('Finesse (Remix) [feat. Cardi B]','Bruno Mars',0.704),
('Back To You - From 13 Reasons Why ? Season 2 Soundtrack','Selena Gomez',0.601),
('Let You Down','NF',0.656),
('Call Out My Name','The Weeknd',0.489);

