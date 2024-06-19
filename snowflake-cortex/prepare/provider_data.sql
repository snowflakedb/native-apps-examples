USE ROLE ACCOUNTADMIN;
CREATE DATABASE IF NOT EXISTS ;
CREATE SCHEMA IF NOT EXISTS SPOTIFY_CORTEX_DB.SPOTIFY_CORTEX_SCHEMA;
CREATE OR REPLACE TABLE SPOTIFY_CORTEX_DB.SPOTIFY_CORTEX_SCHEMA.SPOTIFY_PROVIDER_DATA(
    track_name VARCHAR,
    artists_name VARCHAR,
    artist_count INTEGER,
    released_year INTEGER,
    released_month INTEGER,
    released_day INTEGER,
    in_spotify_charts INTEGER,
    streams INTEGER,
    danceability_% INTEGER
);
INSERT INTO SPOTIFY_CORTEX_DB.SPOTIFY_CORTEX_SCHEMA.SPOTIFY_PROVIDER_DATA VALUES
("Seven (feat. Latto) (Explicit Ver.)","Latto, Jung Kook",2,2023,7,14,147,141381703,80),
("LALA","Myke Towers",1,2023,3,23,48,133716286,71),
("vampire","Olivia Rodrigo",1,2023,6,30,113,140003974,51),
("Cruel Summer","Taylor Swift",1,2019,8,23,100,800840817,55),
("WHERE SHE GOES","Bad Bunny",1,2023,5,18,50,303236322,65),
("Sprinter","Dave, Central Cee",2,2023,6,1,91,183706234,92),
("Ella Baila Sola","Eslabon Armado, Peso Pluma",2,2023,3,16,50,725980112,67),
("Columbia","Quevedo",1,2023,7,7,43,58149378,67),
("fukumean","Gunna",1,2023,5,15,83,95217315,85),
("La Bebe - Remix","Peso Pluma, Yng Lvcas",2,2023,3,17,44,553634067,81),
("un x100to","Bad Bunny, Grupo Frontera",2,2023,4,17,40,505671438,57),
("Super Shy","NewJeans",1,2023,7,7,55,58255150,78),
("Flowers","Miley Cyrus",1,2023,1,12,115,1316855716,71),
("Daylight","David Kushner",1,2023,4,14,98,387570742,51),
("As It Was","Harry Styles",1,2022,3,31,130,2513188493,52),
("Kill Bill","SZA",1,2022,12,8,77,1163093654,64),
("Cupid - Twin Ver.","Fifty Fifty",1,2023,2,24,77,496795686,78),
("What Was I Made For? [From The Motion Picture 'Barbie']","Billie Eilish",1,2023,7,13,104,30546883,44),
("Classy 101","Feid, Young Miko",2,2023,3,31,40,335222234,86),
("Like Crazy","Jimin",1,2023,3,24,68,363369738,63),
("LADY GAGA","Gabito Ballesteros, Junior H, Peso Pluma",3,2023,6,22,26,86444842,65),
("I Can See You (Taylor\'s Version) (From The ","Taylor Swift",1,2023,7,7,38,52135248,69),
("I Wanna Be Yours","Arctic Monkeys",1,2013,1,1,110,1297026226,48),
("Peso Pluma: Bzrp Music Sessions, Vol. 55","Bizarrap, Peso Pluma",2,2023,5,31,40,200647221,85),
("Popular (with Playboi Carti & Madonna) - The Idol Vol. 1 (Music from the HBO Original Series)","The Weeknd, Madonna, Playboi Carti",3,2023,6,2,87,115364561,85),
("SABOR FRESA","Fuerza Regida",1,2023,6,22,26,78300654,79),
("Calm Down (with Selena Gomez)","Rema, Selena G",2,2022,3,25,77,899183384,80),
("MOJABI GHOST","Tainy, Bad Bunny",2,2023,6,29,40,61245289,81),
("Last Night","Morgan Wallen",1,2023,1,31,19,429829812,52),
("Dance The Night (From Barbie The Album)","Dua Lipa",1,2023,5,25,101,127408954,67),
("Rush","Troye Sivan",1,2023,7,13,78,22581161,74),
("TULUM","Peso Pluma, Grupo Frontera",2,2023,6,28,34,52294266,56),
("Creepin'","The Weeknd, 21 Savage, Metro Boomin",3,2022,12,2,88,843957510,71),
("Anti-Hero","Taylor Swift",1,2022,10,21,56,999748277,64),
("TQG","Karol G, Shakira",2,2023,2,23,49,618990393,72),
("Los del Espacio","Big One, Duki, Lit Killah, Maria Becerra, FMK, Rusherking, Emilia, Tiago pzk",8,2023,6,1,31,123122413,81),
("Fragil (feat. Grupo Front","Yahritza Y Su Esencia, Grupo Frontera",2,2023,4,7,34,188933502,61),
("Blank Space","Taylor Swift",1,2014,1,1,53,1355959075,75),
("Style","Taylor Swift",1,2014,1,1,42,786181836,60),
("TQM","Fuerza Regida",1,2023,5,19,28,176553476,79),
("El Azul","Junior H, Peso Pluma",2,2023,2,10,25,354495408,56),
("Sunflower - Spider-Man: Into the Spider-Verse","Post Malone, Swae Lee",2,2018,10,9,78,2808096550,76),
("I'm Good (Blue)","Bebe Rexha, David Guetta",2,2022,8,26,80,1109433169,56),
("See You Again","Tyler, The Creator, Kali Uchis",3,2017,7,21,64,1047101291,56),
("Barbie World (with Aqua) [From Barbie The Album]","Nicki Minaj, Aqua, Ice Spice",3,2023,6,23,80,65156199,77),
("Angels Like You","Miley Cyrus",1,2020,11,27,19,570515054,67),
("I Ain't Worried","OneRepublic",1,2022,5,13,76,1085685420,71),
("Die For You","The Weeknd",1,2016,11,24,59,1647990401,59),
("Starboy","The Weeknd, Daft Punk",2,2016,9,21,79,2565529693,68),
("Die For You - Remix","Ariana Grande, The Weeknd",2,2023,2,24,47,518745108,53),
("El Cielo","Feid, Myke Towers, Sky Rompiendo",3,2023,6,2,38,107753850,72),
("Baby Don't Hurt Me","David Guetta, Anne-Marie, Coi Leray",3,2023,4,6,66,177740666,60),
("AMARGURA","Karol G",1,2023,2,24,39,153372011,92),
("(It Goes Like) Nanana - Edit","Peggy Gou",1,2023,6,15,59,57876440,67),
("Another Love","Tom Odell",1,2012,10,15,83,1813673666,45),
("Blinding Lights","The Weeknd",1,2019,11,29,69,3703895074,50),
("Moonlight","Kali Uchis",1,2023,2,24,42,256483385,64),
("La Bachata","Manuel Turizo",1,2022,5,26,45,1214083358,84),
("S91","Karol G",1,2023,7,14,41,16011326,86),
("cardigan","Taylor Swift",1,2020,7,24,29,812019557,61),
("Ta OK","dennis, MC Kevin o Chris",2,2023,5,4,15,111947664,86),
("Boy's a liar Pt. 2","PinkPantheress, Ice Spice",2,2023,2,3,41,156338624,70),
("Left and Right (Feat. Jung Kook of BTS)","Charlie Puth, BTS, Jung Kook",3,2022,6,24,39,720434240,88),
("BESO","Rauw Alejandro, ROSAL�",2,2023,3,24,50,357925728,77),
("Hey Mor","Ozuna, Feid",2,2022,10,6,38,674072710,90),
("Yellow","Chris Molitor",1,1999,1,1,43,1755214421,43),
("Karma","Taylor Swift",1,2022,10,21,23,404562836,64),
("People","Libianca",1,2022,12,2,56,373199958,59),
("Overdrive","Post Malone",1,2023,7,14,36,14780425,56),
("Enchanted (Taylor's Version)","Taylor Swift",1,2023,7,7,24,39578178,51),
("BABY HELLO","Rauw Alejandro, Bizarrap",2,2023,6,23,35,54266102,77),
("Heat Waves","Glass Animals",1,2020,6,28,63,2557975762,76),
("golden hour","JVKE",1,2022,7,15,36,751134527,51),
("Sweater Weather","The Neighbourhood",1,2012,5,14,61,2282771485,61),
("Quevedo: Bzrp Music Sessions, Vol. 52","Bizarrap, Quevedo",2,2022,7,6,45,1356565093,62),
("Viva La Vida","Coldplay",1,2008,1,1,62,1592909789,49),
("Here With Me","d4vd",1,2022,7,17,23,635412045,58),
("Unholy (feat. Kim Petras)","Sam Smith, Kim Petras",2,2022,9,22,42,1230675890,71),
("Yandel 150","Yandel, Feid",2,2022,12,20,38,585695368,78),
("CORAZON VACIO","Maria Becerra",1,2023,6,22,20,43857627,68),
("Riptide","Vance Joy",1,1975,1,1,55,2009094673,48),
("Until I Found You (with Em Beihold) - Em Beihold Version","Em Beihold, Stephen Sanchez",2,2022,4,22,30,600976848,34),
("Novidade na area","Mc Livinho, DJ Matt D",2,2023,6,23,9,39709092,63),
("Back To December (Taylor's Version)","Taylor Swift",1,2023,7,7,17,39228929,50),
("STAY (with Justin Bieber)","Justin Bieber, The Kid Laroi",2,2021,7,9,36,2665343922,59),
("El Merengue","Marshmello, Manuel Turizo",2,2023,3,3,44,223633238,78),
("Someone You Loved","Lewis Capaldi",1,2018,11,8,53,2887241814,50),
("Me Porto Bonito","Chencho Corleone, Bad Bunny",2,2022,5,6,43,1440757818,91),
("Makeba","Jain",1,2015,6,22,53,165484133,82),
("MONTAGEM - FR PUNK","Ayparia, unxbected",2,2012,6,20,50,58054811,63),
("Fast Car","Luke Combs",1,2023,3,24,12,157058870,71),
("What It Is (Solo Version)","Doechii",1,2023,3,17,25,95131998,74),
("Coco Chanel","Bad Bunny, Eladio Carrion",2,2023,3,17,38,250305248,68),
("Don't blame me","Taylor Swift",1,2017,11,8,23,685032533,62),
("Still With You","Jung Kook",1,2020,6,5,39,38411956,53),
("All My Life (feat. J. Cole)","J. Cole, Lil Durk",2,2023,5,12,23,144565150,83),
("Say Yes To Heaven","Lana Del Rey",1,2023,3,17,46,127567540,49),
("Snooze","SZA",1,2022,12,9,25,399686758,56),
("Summertime Sadness","Lana Del Rey",1,2011,1,1,52,983637508,56),
("Take Two","BTS",1,2023,6,9,47,118482347,62),
("Lover","Taylor Swift",1,2012,1,1,23,882831184,43);

