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

---

## Helper Methods
There are a few methods in **Instructors/views/utils.py** which should be used when saving, converting, rendering datetimes.

### Method 1
