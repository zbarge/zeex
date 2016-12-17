#!usr/bash

$ENV_DIR = "C:/Users/Zeke/Google Drive/dev/python/zeex/venv"
$OUTPUT_DIR = "C:/Users/Zeke/Google Drive/dev/python/zeex/docs/build"
$SOURCE_DIR = "C:/Users/Zeke/Google Drive/dev/python/zeex/zeex"

$QTPANDAS_DIR = "C:/Users/Zeke/Google Drive/dev/python/qtpandas"

$ENV_DIR/Scripts/activate

sphinx-apidoc -o $OUTPUT_DIR $SOURCE_DIR