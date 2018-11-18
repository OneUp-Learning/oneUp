# How to Compile React Javascript Files 

## Prerequisites
* NPM needs to be installed
## Compiling React Files
The file **package.json** contains commands that can compile the react chat app javascript files different ways.
### Single Build
Run the command `npm run dev` to compile the chat app javascript files into the static folder for django. The command should be run in this current directory.

> This command will need to be ran after every change to the react javascript files. To auto compile after every change see Watch Build

### Watch Build
Run the command `npm run watch` to compile the chat app javascript files automatically after every change to any javascript file in the chat app. Probably want to do this command in a seperate terminal.

### Production Build
Run the command `npm run build` to compile the chat app javascript files for production.

## Modifying Compiled Output Directories
The output directories are defined in two files depending on the environment.
### Development Environment
Running a single build or watch build will both output the javascript files in the same directories. The directories are defined in **dev.config.js** in this directory.

> Main parts are the entry (the file to compile) and output path (directory where to place the entry)

### Production Environment
The entry and output directory for the production build is set in **package.json** in this directory. As of now, it is only setup to export one file. In the future, there should be a *prod.config.js* file which has configuration for production.



