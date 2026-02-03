#!/bin/env bash

if [ -z "$1" ]; then
    echo "Usage: ./script.sh [-mp4 | -gif]"
    exit 1
fi

mkdir -p images
rm -f images/*

if [ "$1" != "-clean" ]; then
    python3 main.py $2
fi

case "$1" in
    -gif)
        echo "Exporting as GIF..."
        ffmpeg -framerate 30 -i images/frame%d.ppm -vf "fps=30,scale=400:-1:flags=lanczos,split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse" images/output.gif
        OUT_FILE="output.gif"
        ;;
    -mp4)
        echo "Exporting as MP4..."
        ffmpeg -framerate 30 -i images/frame%d.ppm -c:v libx264 -pix_fmt yuv420p -vf "scale=trunc(iw/2)*2:trunc(ih/2)*2" images/output.mp4
        OUT_FILE="output.mp4"
        ;;
    -clean)
        echo "Cleaning up folders..."
        rm -rf images/ output/
        echo "Cleaning done!"
        exit 0
        ;;
    *)
        echo "Invalid option: $1"
        echo "Use -mp4 or -gif"
        exit 1
        ;;
esac

mkdir -p output/
mv "images/$OUT_FILE" "output/$OUT_FILE"
rm -f images/frame*
rm -rf images/

echo "Done! File saved to output/$OUT_FILE"