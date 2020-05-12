# Creating New Pages in Oneup
When creating a new page there are a few files which need to be created and edited.

## General Information
Mostly every page in Oneup platform has a Python **view** file and a HTML file that goes with it. 

The **view** is used to handle any database queries, collecting data, processing data, etc. The **view** can also send data to the HTML.

The HTML file is used to visually display data sent from the **view** in the browser. HTML file can also send data back to the **view**. Data that is sent from the **view** to the HTML will not update after it has been sent. If you need dynamic data, the JavaScript in the HTML should make a AJAX call to pull data from the **view**.

The **urls.py** file is used to link the **view** and HTML file together. This file should be already created and is in the root of the apps folders: Instructors, Badges, Students, Chat, Administrators, and oneUp.


## Creating the View
The view is just a python method which will return a render call with the HTML page to render and the data (context dictionary).

A generic view can look like this:
```python
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from Instructors.views.utils import initialContextDict

@login_required
def demo(request):   
    context_dict, course = initialContextDict(request)
    ...
    context_dict['my_data'] = 2
    ...
    return render(request, 'Instructors/demo.html', context_dict)
```
The ```@login_required``` decorator is used to validate if the user is currently logged in. If the user is not logged in they cannot access this method.

The method signature should take in request as a parameter.

The first line of the method is used to get various informatation about the user and which course they are in. All that data is stored in the context_dict dictionary variable.

> Note: If the view is for **students** instead of ```initialContextDict``` it should be ```studentInitialContextDict```

After that line, you can populate the context_dict variable which will be sent to the HTML.

Lastly, you will need to return what HTML to send the data to.

> Note: This is one way of writing a **view**. Check out other **views** for more examples

## Creating the HTML
The HTML is located in the **templates/** folder.
The basic structure can look like this:

```html
<!DOCTYPE html>
<html lang="en">
    <head>
        {% include 'scripts.html' %}
    </head>
    <body>
        {% include 'heading.html' %}
        <main>
            <!-- Your page elements --->
            <p>My data: {{my_data}}</p>
        </main>
        {% include 'footer.html' %}
    </body>
    <script>
    // Your custom scripts
    </script>
</html>
```
The curly braces notation if used by django to load in different parts of HTML into another. Here we are loading in the **scripts.html** page into the head tags. 

Here the ```{{my_data}}``` will return the value that is stored in the context_dict that was sent to this page. If the context_dict does not contain the **my_data** key, then the value will be empty.

If the HTML page is being used for students the ```{% include 'heading.html' %}``` needs to be changed to ```{% include 'stheading.html' %}``` in order to use the student navbar instead of the instructors. 

> Note: Look at the other HTML pages to see more examples

## Linking the View and HTML
To link the two together you will need to edit the corresponding **urls.py** file.

You will need to create another entry in the urlpatterns list like so:

```python
 url(r'^demo', demo, name='my-demo-page')
 ```
 The first parameter is the last part of url that is display in the url bar of the browser.

 The second parameter is the Python method to call when visiting the url. 
 > Note: Be sure to import the method at the top of the urls.py file

 The last parameter is used to give the route a name.
