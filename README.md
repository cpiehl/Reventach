# Reventach
Lamborghini Reventon Tachometer for Assetto Corsa

## Screenshots and Video

![screenshot](https://i.imgur.com/CvUAOzA.jpg)
[![youtube](https://i.imgur.com/tLQJtjj.png)](https://www.youtube.com/watch?v=a0fESLSw3-o)]

## Installation

1. Extract the **Reventach** folder into steamapps\\common\\assettocorsa\\apps\\python\\
2. Enable the app in Options > General
3. Enable the app in-game

#### Addon cars

You can add addon cars to a custom file `cardata-custom.json` that won't be overwritten by updates.

For example, adding [garyjpaterson's Dallara FX17](http://www.racedepartment.com/downloads/dallara-fx-17.13928/) would look like this:

```
{
	"dallara_fx17": { "maxRPM": 14200, "gears": 6 }
}
```

Adding any more cars follows the same pattern as `cardata.json`, for example a fictional Abarth 500 Stage 2:

```
{
	"dallara_fx17": { "maxRPM": 14200, "gears": 6 },
	"abarth500_s2": { "maxRPM": 6500, "gears": 5 }
}
```

More examples can be found in the full `cardata.json` file.
