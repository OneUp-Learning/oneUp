#!/bin/sh
#
# A small script which compiles the oneup SASS file to CSS and renames it based on which mode is selected
# SASS must be installed in order for this to work
#

dark_mode=0
output_name="materialize.css"
script_path="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
sass_location="${script_path}/static/assets/sass/materialize.scss"

for arg in "$@"
do
    if [ "$arg" = "--help" ] || [ "$arg" = "-h" ]
    then
        echo "Builds the SASS file and places the compiled CSS into the oneup assets folder."
        echo "Usage: buildtheme [-d | -darkmode] [-h | --help]"
        echo 
        echo "━━━ \033[1mInput and Output\033[0m ━━━━━━━━━━━━━━━━━━━"
        echo "-d, --darkmode        Saves the compiled CSS as dark-materialize.css. Note: actual darkmode is set in static/assets/sass/components/_variables.scss"
        echo "-h, --help            The help screen"
        exit 0
    elif [ "$arg" = "--darkmode" ] || [ "$arg" = "-d" ]
    then
        dark_mode=1
        output_name="dark-materialize.css"
    else 
        echo "Usage: buildtheme [-d | -darkmode] [-h | --help]"
        echo 
        echo "━━━ \033[1mInput and Output\033[0m ━━━━━━━━━━━━━━━━━━━"
        echo "-d, --darkmode        Saves the compiled CSS as dark-materialize.css. Note: actual darkmode is set in static/assets/sass/components/_variables.scss"
        echo "-h, --help            The help screen"
        exit 0
    fi
done

build_location="${script_path}/static/assets/css/${output_name}"
if [ "$dark_mode" = "1" ]
then
    echo "Building CSS with Dark Mode..."
    echo "Sass file: $sass_location"
    echo "Build file: $build_location"
    sass $sass_location $build_location
else
    echo "Building CSS..."
    echo "Sass file: $sass_location"
    echo "Build file: $build_location"
    sass $sass_location $build_location
fi

