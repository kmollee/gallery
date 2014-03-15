#!/bin/bash

compressor="java -jar /bin/yuicompressor-2.4.8.jar"
static_dir="gallery/static"

for file in "chosen-1.1.0/chosen.jquery.js" "chosen-1.1.0/chosen.css" "css/gallery.css" "css/reset.css" "js/gallery.js"
do
    echo $file
    new_file="${file%.*}.min.${file##*.}"
    $compressor -o "$static_dir/$new_file" "$static_dir/$file"
done
