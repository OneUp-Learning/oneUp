# React Chat App Development 
This file describes how to begin developing using react on the chat app

## Development Scripts
All the development javascript files are in the `src` folder under this folder. All react components are combined into one file: `chat-app.js`. This file just simply imports the `App.js` file

## Running the Code
Webpack is used to combine all the React components into one native JavaScript file that will be put in this django static folder: 
> **static/chat/frontend/**

To combine these files you will need to run a command. These commands are defined in the `package.json` found in this folder. Specifically, in the scripts object
> **NOTE: all commands should be ran in the react folder**

### Dev Command
The dev command is used to compile the React components once
> **npm run dev**

### Watch Command
The watch command is used to compile the React components every time you save any of the React JavaScript files
> **npm run watch**

### Build Command
The build command compiles the React components to be ready for production. (Haven't tested fully)
> **npm run build**

### Creating Your Own
You can easily create your own command by adding a new entry to the scripts object. Just give it a name and a command to run 
:)

## Changing the Output
If you want to modify the location of where the compiled JavaScript file will get placed, you will need to modify/create a webpack configuration

There are two configurations that are already created:

* `dev.config.js`
* `prod.config.js`

The producation configuration is similar but the mode is change to `production` instead of `development`

## Webpack Configuration
The main part of the configuration file is the entry point and output

### Entry
The entry takes in key-value pairs of the name and actual JavaScript file.
These should be the files that you want to compile

### Output
The output takes in a path which is the target directory of the compiled file and the actual name you want to give it
> **NOTE: [name] can be used to get the name key you gave it in the entry key-value object**
