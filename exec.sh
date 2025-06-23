echo " Cleaning directory"
rm -r ./frames
mkdir frames
rm output.mp4
rm output_with_audio.mp4
rm sound_logs.txt

echo "Starting generation"
echo "to creator : Make sure python is loaded if using conda lazyloading"
python main.py
echo "Generating vieo"
ffmpeg -framerate 60 -i frames/frame_%05d.png -c:v libx264 -pix_fmt yuv420p output.mp4
echo "Generating Audio"
python sound.py
echo "Adding Audio"
# ffmpeg -i output.mp4 -i final_audio.wav -c:v copy -c:a aac -shortest output_with_audio.mp4
ffmpeg -i output.mp4 -i final_audio.wav -c:v copy -c:a libmp3lame -q:a 2 -shortest output_with_audio.mp4

echo "Publishing"
python uploader.py