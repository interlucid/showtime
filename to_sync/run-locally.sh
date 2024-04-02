# kill any ghost programs just in case something got left hanging
sudo killall -9 python3 flask
cd ~/Music/neopixels
# make sure song list the webpage will use is up to date
python3 generate_song_list.py
# start the actual controller
flask --app song_server run --host=0.0.0.0 --port 5001 --debug