# <div align="center">OBJECTIVE
<br>
[pypi](https://pypi.org/manage/projects/)

Take MLB data and statistics and use that to create a "MLB the Show" style player ranking with attributes such as velocity, movement, power, contact, as well as an overall.

These will be calculated from several carefully selected stats or points of data, and more commonly, combined together with a formula to capture the best essence of what an attribute means as a combination of raw skill and past performance.

This can and currently is applied to every healthy, active player on a specific team, and thus creates a team rating. This will, in future, be used in a ML algorithm to roughly predict the end-season standings, I do ***not*** expect this to be extremely accruate or reliable, as of yet that is.

<br>

##### <div align="center"> CREATING PITCHER METRICS <div>

<br>

1. Create raw pitcher attributes, velocity, movement, and command. To do this there needs to be a distinction between what is indicative of raw skill versus performance.

- For **velocity** it is straight foward, it is the median velocity of a pitchers fastball-type pitches (Four-seam, Sinker, Cutter. * Two seam was labeled under sinker in the dataset.), ranked as a percentile from across the league. So a pitcher who on average throws low-mid 90's is about 50th percentile. It is a bit lower than pure 4-Seam velo of course.
<br>
- For **movement** it requires a little more engineering. The idea is to essentially get the average amount of ***induced movement***, which is the measure of how much a pitch breaks islotated from gravity. Now we seperate the averages across three categories, velocity stuff, breaking stuff, and offspeed stuff. Next we get our percentiles and combine these categories and get the average. The categories are weighted with more influence being on breaking and less of velo pitches. If a pitches fastball doesn't break that much, but his curveball does, his score will not be affected by the low fastball break too much.
<br>
- **Command** was thankfully straightfoward due to the **open-command** library, which measures the difference in pitch location, versus the intended location, unfortunately as of right now I only have data dating back to 2023.

<br>

- **OVR** is derived from WAR.


>##### <div align="center"> CREATING HITTER METRICS <div>

- **Power** is created from EV50 Barrel% and ISO

- **Contact** is the the combined inside and outside of the zone contact %, and the combined batting avg and expected batting average. Will revise these.

>Maybe Later: Estimate pitcher stamina.
