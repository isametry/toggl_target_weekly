Toggl Target
============

Forked from the original toggle_target by @mos3abof, modified for **simpler usage** and for functioning **weekly** (not monthly).


Installation (on macOS)
---------------------

1. Download the script _"toggl_target_weekly.py"_.
2. Open the script in a text editor and configure the following: 
   * On **line 16,** place your actual Toggl API token (can be found on https://track.toggl.com/profile, bottom of the page).
   * On **line 19,** choose your weekly hour goal.

3. If you don't have pip, run in the Terminal:
```
python3 -m ensurepip
```
4. Then run the command below to install additional required packages:
```
pip3 install python-dateutil requests
```




Usage
-----

To use the script run the following command :

```
python3 toggl_target_weekly.py
```


Contributors
-------------

* [@mos3abof](http://www.mos3abof.com)
* [@mtayseer](http://www.mtayseer.net)
* [@isametry](http://github.com/isametry/)

License
-------

```
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
```
