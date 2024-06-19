USE ROLE ACCOUNTADMIN;
CREATE DATABASE IF NOT EXISTS SPOTIFY_CORTEX_DB;
CREATE SCHEMA IF NOT EXISTS SPOTIFY_CORTEX_DB.SPOTIFY_CORTEX_SCHEMA;
CREATE OR REPLACE TABLE SPOTIFY_CORTEX_DB.SPOTIFY_CORTEX_SCHEMA.SPOTIFY_PROVIDER_DATA(
    track_name VARCHAR,
    artists_name VARCHAR,
    artist_count INTEGER,
    released_year INTEGER,
    released_month INTEGER,
    released_day INTEGER,
    in_spotify_charts INTEGER,
    spotify_streams INTEGER,
    danceability_percentage INTEGER
);
INSERT INTO SPOTIFY_CORTEX_DB.SPOTIFY_CORTEX_SCHEMA.SPOTIFY_PROVIDER_DATA VALUES
('Seven \(feat. Latto\) \(Explicit Ver.\)','Latto, Jung Kook',2,2023,7,14,147,141381703,80),
('LALA','Myke Towers',1,2023,3,23,48,133716286,71),
('vampire','Olivia Rodrigo',1,2023,6,30,113,140003974,51),
('Cruel Summer','Taylor Swift',1,2019,8,23,100,800840817,55),
('WHERE SHE GOES','Bad Bunny',1,2023,5,18,50,303236322,65),
('Sprinter','Dave, Central Cee',2,2023,6,1,91,183706234,92),
('Ella Baila Sola','Eslabon Armado, Peso Pluma',2,2023,3,16,50,725980112,67),
('Columbia','Quevedo',1,2023,7,7,43,58149378,67),
('fukumean','Gunna',1,2023,5,15,83,95217315,85),
('La Bebe - Remix','Peso Pluma, Yng Lvcas',2,2023,3,17,44,553634067,81);