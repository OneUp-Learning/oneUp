# Helpful Tips/Notes

## Disable constant notifications logging in console
If you are trying to find output in the terminal when running the server the constant notification logging can get annoying. 

You can disable this logging by going to 
```/lib/python3.7/site-packages/channels/management/commands/runserver.py```. This file should be in the lib folder in your virtual environment

Change to match these lines in the file:
```python
....
# Utilize terminal colors, if available
if 200 <= details["status"] < 300:
    # Put 2XX first, since it should be the common case
    if '/notifications/api/update/?flag=' in details['path']:
        return
    logger.info(self.style.HTTP_SUCCESS(msg), details)
....
```
> You can also disable more daphne logging by going to ```/lib/python3.7/site-packages/daphne/http_protocol.py```

## Responsive Mobile Tables
When using the class, ```responsive-table```, on the table element the theme will convert the table to a mobile friendly version on mobile. When there is no data in the table, the table styling messes up. 

Place the code below the end of the first **tbody** tag to fix this:
```html
<tbody class="hide-on-large-only mobile-table-padding"></tbody>
```

## Changing the Notification Icons
When a user recieves a notification as of now a bubble pops up next to the notification icon. There is commented out code in the student and instructor heading which can hide the bubble and use a different look.

The snippet below shows where the change needs to be made to enable the other look. There should only be one enabled at a time.

```javascript
// Show/hide unread counts for notification bubble and mobile badge
if(unread_count == 0){
    // Desktop bubble
    icon_element.removeClass("notification-icon-notify");
    icon_element.addClass("notification-icon");
    
    // Desktop bell icon - If enabled, comment out the two lines above 
    // icon_element.text("notifications");

    ...

} else {

    // Desktop bubble
    icon_element.removeClass("notification-icon");
    icon_element.addClass("notification-icon-notify");

    // Desktop active bell icon - If enabled, comment out the two lines above 
    // icon_element.text("notifications_active");
    
    ...
    
}
```
> More icons are available at https://material.io/resources/icons/?style=baseline and see how to use them at http://archives.materializecss.com/0.100.2/icons.html

## Making Changes to the Main Navbars
If you are adding links or making changes to the navbar for either instructors or students be sure to make changes to the mobile html code as well. The files: ```stheading.html``` and ```heading.html``` both have a mobile and desktop version for the navbar.
