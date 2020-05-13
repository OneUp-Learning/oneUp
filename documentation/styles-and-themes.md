# Working with Styles and Themes in Oneup
Oneup styles are mostly made from SASS which is then compiled to CSS. There are also some inline CSS on a lot of HTML pages as well.

Oneup also features different modes: Light and Dark. These modes only affect the styles that come from SASS. 

## Making Changes to SASS files
The sass files are located in **static/assets/sass/**. Different components of the theme is seperated into different files. The main file which has all the colors is called **_variables.scsss**.

In **_variables.scsss**, you can change all the colors for mostly all the different components in the theme such as cards, navbars, etc.

In **_global.scsss**, at the bottom we have custom classes which can be applied globally. There are some classes there that was taken from the HTML in order to reduce redundant changes across the platform. If you see places where we use the same classes in HTML at multiple places, placing the code in this file is a good way to start.

> Note: Flashcards styles were moved to the **_cards.scss** file

## Compiling Changes & Building the CSS
Once you make your changes you may need to compile for both dark mode and light mode.
> Note: **SASS** must be installed in order to build the CSS

There is a script called ```buildtheme.sh``` in the oneup directory which will compile the files for you and will place them in the correct directories. You can do ```./buildtheme.sh --help``` for detail usage.

> Note: Make sure ```buildtheme.sh``` is executable

To build the **light mode**:
- Make sure ```$dark-mode: false;``` in **_variables.scsss** at the top of the file
- Run ```./buildtheme.sh``` in your terminal

To build the **dark mode**:
- Make sure ```$dark-mode: true;``` in **_variables.scsss** at the top of the file
- Run ```./buildtheme.sh -d``` in your terminal

After building and compiling you should see your changes in the browser. You may need to hard reload if you don't see the changes.