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

You will usually want to save the datetime object that is **localized** (being timezone aware). 

When retrieving from the database, django automatically displays the datetime object in the HTML with the correct timezone. 

If you are in need to **filter** or **compare aganist other dates**, you should first convert the datetime object from the model instance to a **local datetime object**. 

If you are loading the datetime object into a input field, for example the datetime picker, you should first convert the local datetime object to a string before passing it to the HTML

---

## Helper Methods
There are a few methods in **Instructors/views/utils.py** which should be used when saving, converting, rendering datetimes.

### Method 1
def current_utctime():
    ''' Return current utc datetime object '''
    return timezone.now()

def current_localtime(tz=timezone.get_current_timezone()):
    ''' Returns current local datetime object '''
    if type(tz) == str:
        tz = pytz.timezone(tz)

    return timezone.localtime(current_utctime(), timezone=tz)

def datetime_to_local(db_datetime, tz=timezone.get_current_timezone()):
    ''' Converts datetime object to local '''
    if not db_datetime:
        return None

    if timezone.is_naive(db_datetime):
        db_datetime = timezone.make_aware(db_datetime)

    if type(tz) == str:
        tz = pytz.timezone(tz)
        
    return timezone.localtime(db_datetime, timezone=tz).replace(microsecond=0)

def datetime_to_utc(db_datetime):
    ''' Converts datetime object to utc '''
    if not db_datetime:
        return None
        
    return db_datetime.replace(microsecond=0).astimezone(timezone.utc)

def str_datetime_to_local(str_datetime, to_format="%m/%d/%Y %I:%M %p", tz=timezone.get_current_timezone()):
    ''' Converts string datetime to local timezone datetime object '''
    return datetime_to_local(datetime.datetime.strptime(str_datetime, to_format), tz=tz)

def str_datetime_to_utc(str_datetime, to_format="%m/%d/%Y %I:%M %p"):
    ''' Converts string datetime to utc datetime object '''
    return datetime_to_utc(datetime.datetime.strptime(str_datetime, to_format))

def datetime_to_selected(db_datetime, to_format="%m/%d/%Y %I:%M %p"):
    ''' Converts datetime object to what was actually selected in the interface '''
    print(type(db_datetime))

    if type(db_datetime) == datetime.date:
        db_datetime = datetime.datetime.combine(db_datetime, datetime.datetime.min.time())
        
    if timezone.is_naive(db_datetime):
        db_datetime = timezone.make_aware(db_datetime)

    return timezone.make_naive(db_datetime.replace(microsecond=0)).strftime(to_format)

def date_to_selected(db_date, to_format="%m/%d/%Y"):
    ''' Converts date object to what was actually selected in the interface '''
    return db_date.strftime(to_format)