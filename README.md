# merisaa
Hakee Ilmatieteen laitoksen Merisään ja muuttaa sen puheeksi samassa formaatissa kuin radiossa

# Asennus

Asenna Miniconda ja Mamba ensiksi.

```bash
git clone https://github.com/mikkoim/merisaa
cd merisaa
mamba env create -f environment.yaml
conda activate merisaa
```


# Hae ajantasainen Merisää 
 
```bash
python scripts/get_merisaa.py --asema_file data/rannikkoasemat_litteroitu.txt
```
Ulostulona tekstitiedostot joissa säätiedotus merenkulkijoille ja sää rannikkoasemilla.

# Muuta säätiedotukset puheeksi
```bash
python scripts/tts.py --input out_01_saatiedotus_merenkulkijoille.txt --output out_01_saatiedotus_merenkulkijoille.wav
python scripts/tts.py --input out_02_saa_rannikkoasemilla.txt --output out_02_saa_rannikkoasemilla.wav
```

# Yhdistä audiotiedostot ja tee video
```bash
ffmpeg -f concat -safe 0 -i concatenate.txt -c copy out_03_full_audio.wav

# Audio -> Video 
ffmpeg -loop 1 -i majakka.png -i out_03_full_audio.wav -vcodec libx264 -shortest out.mp4
```

# Streaming

Aloita uusi live stream youtubessa ja kopioi stream key. Aja sitten seuraava komento:

```bash
python scripts/stream.py -k <youtube_stream_key>
```