# Working with Time in Oneup
## Currently Supported Timezones
| Timezone          | String Value            |
| -------------     |:-----------------------:| 
| Eastern (EST)     | `America/New_York`      |
| Central (CST)     | `America/Chicago`       |
| Mountain (MST)    | `America/Denver`        |
| Pacific (PST)     | `America/Los_Angeles`   |

---

## Basic Information
Each univeristy has a timezone associated with it that was selected through the admin portal. The timezone is activated when the user selects a course and is saved in the current request session which can be retrieved anytime like so:
```python
request.session['django_timezone']
```
> See **Administrators/views/setCourseView.py**

You will usually want to save the datetime object that is **localized** (being timezone aware). You can use the local methods below to localize the datetimes. 

When retrieving from the database, django automatically displays the datetime object in the HTML with the correct timezone. 

If you are in need to **filter** or **compare aganist other dates**, you should first convert the datetime object from the model instance to a **local datetime object**. 

If you are loading the datetime object into a input field, for example the datetime picker, you should first convert the local datetime object to a string before passing it to the HTML

---

## Helper Methods
There are a few methods in **Instructors/views/utils.py** which should be used when saving, converting, rendering datetimes.

### Getting the Current Datetime
There are two methods which will return the current time in UTC or in the current timezone: ```current_utctime``` and ```current_localtime``` 

If you need to get the current time for a specific timezone, pass the timezone as a argument to the ```current_localtime``` method like so:

```python
current_localtime(tz="America/Denver")
```

### Converting String to Datetime
There are two methods which can convert a string representation of a date time object: ```str_datetime_to_utc``` and ```str_datetime_to_local```

These methods accept another argument which is the format of the string. That argument is used to convert the string to datetime. The default format is ```%m/%d/%Y %I:%M %p```. You can also change this format to match the date only if you are trying to convert a string that only has the date.

Again the local version accepts a timezone which can be used to convert to a specific timezone

Here is a example one way of using the methods:
```python
str_datetime_to_local(my_datetime_str, to_format="%m/%d/%Y %I:%M:%S %p", tz="America/Los_Angeles")
```

> If you only need to convert a datetime object to utc or another timezone you can use the ```datetime_to_utc``` and ```datetime_to_local``` methods to do that

### Converting Datetime to String
There are two methods which can convert a date or datetime object to a string: ```datetime_to_selected``` and ```date_to_selected```

These two methods accepts a format like the other. These methods should be used when you need to display the date or datetime in the datepicker or a field that can be edited by the user.

Here is a example one way of using the methods:
```python
datetime_to_select(my_datetime_obj, to_format="%m/%d/%Y %I:%M:%S %p")
```