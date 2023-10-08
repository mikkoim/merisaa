# Formaatti

Sää rannikkoasemilla tänään kello 12
Haapasaari
lämpötila plus 16 astetta
tuuli etelä-lounaasta 11 m/s
[vesikuuroja, melkein selkeää, pilvistä, utua]
näkyvyyttä 4 km

Mäkiluoto kuusitoista, länsi kaksitoista.
Russarö viisitoista, länsilounas kolmetoista, pilvistä kaksikymmentä.
Rajakari kuusitoista, länsi kaksitoista.
Kumlinge kuusitoista länsi-luode kolmetoista. Hyvä näkyvyys.

Meriveden korkeudet mittausasemilla ...


# Komennot

python get_merisaa.py --asema_file rannikkoasemat_litteroitu.txt

python tts.py --input out_01_saatiedotus_merenkulkijoille.txt --output out_01_saatiedotus_merenkulkijoille.wav
python tts.py --input out_02_saa_rannikkoasemilla.txt --output out_02_saa_rannikkoasemilla.wav

# Combine audio

ffmpeg -f concat -safe 0 -i concatenate.txt -c copy out_03_full_audio.wav

# Audio -> video
ffmpeg -loop 1 -i majakka.png -i out_03_full_audio.wav -vcodec libx264 -shortest out.mp4

# Streaming
rtmp3lite3 -d
ffmpeg -re -i out.mp4 -c:v copy -c:a aac -ar 22050 -ac 1 -preset veryfast -f flv rtmp://localhost/stream