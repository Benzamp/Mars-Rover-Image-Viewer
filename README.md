Created by Ben Harrison using Python and NASA Mars Rover Photos API.

Go to https://api.nasa.gov/ to browse API's and get an API key. Copy and paste this key
in the Settings tab. This key will be saved in the api-key.txt file, so
it will be saved upon closing the application.

Select a Rover, enter a date (sol ex: 1000), then Fetch Images.

Use the Previous and Next arrows to scroll through images.

Click the Download Image button and choose the path. The file will
automatically be named and dated.

Info about sol (solar day):

Source:
https://an.rsl.wustl.edu/help/Content/Using%20the%20Notebook/Concepts%20and%20deep%20dive/Time%20on%20Mars.htm#:\~:text=Sol,a%20location%20on%20the%20planet.

A simple measure of time on Mars is the sol, that is, a solar day. Just
like on Earth, a solar day on Mars is the period of time from one
noontime to the next for a location on the planet. The number of seconds
in a solar day varies throughout the year due to the planet\'s orbit
eccentricity and obliquity (axial tilt). For general purposes, we can
work with an average solar day on Mars being 24:39:35
(hours:minutes:seconds), just as we consider an average solar day on
Earth being 24:00:00, even though we get leap seconds every so often.

Each landed mission uses a sol counter that starts with landing.
Curiosity rover and the InSight and Phoenix landers began counting at
sol 0 on the day of landing. Opportunity and Spirit rovers began
counting at sol 1.

Because a sol (day on Mars) is only slightly longer than an Earth day, a
24-hour clock is a useful method for keeping local time on Mars. As
humans, we already are familiar with 24 hours in a day, even if the
length of an hour is not the same on both planets. We also benefit in
many cases from being able to use computer time functions designed for
24 hour days. Certain tasks require higher precision values, of course,
and we\'ll get there eventually. Local times are presented as day of
mission following landing along with hour, minute, and second.
