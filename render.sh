#!/bin/env bash
rm images/*

python3 main.py
ffmpeg -framerate 30 -i images/frame%d.ppm -vf "fps=30,scale=400:-1:flags=lanczos,split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse" images/output.gif
rm images/frame*