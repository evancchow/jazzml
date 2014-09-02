// Javascript for d3.js for music app visualization.

/* Add the background. */

var fullWidth = $(document).width();
var fullHeight = $(document).height();

/* Initial formatting of the staves. */
var noteViewport = d3.select("#middlerect")
    .append("svg:svg")
    .attr("width", "100%") // i.e. inherit from parent
    .attr("height", "100%")

// Insert the stave lines.
var currLinePos = 5;
var currLineDiff = (100 / 11.0) // for reference later
var midTreblePos = 0; // middle line of treble clef. Useful in future.
var midBassPos = 0; // middle line of bass clef. Useful in future.
for (var i = 0; i < 11; i++) {
    strokeColor = "rgb(0,0,0)"
    if (i == 5) {
	strokeColor = "rgb(254,252,232)" 
    } else if (i == 2) {
	midTreblePos = currLinePos
    } else if (i == 8) {
	midBassPos = currLinePos
    }
    noteViewport.append("svg:line")
	.attr("x1", 0)
	.attr("y1", (currLinePos + "%"))
	.attr("x2", "100%")
	.attr("y2", (currLinePos + "%"))
	.style("stroke", strokeColor)
    currLinePos = Math.round((100 / 11.0) + currLinePos)
}

// Insert treble, base clefs.
var clefs = noteViewport.selectAll("image").data([0])
clefs.enter()
    .append("svg:image")
    .attr("xlink:href", "http://www.clipartbest.com/cliparts/niE/Gxx/niEGxxMiA.png")
    .attr("x", "10")
    .attr("y", "5%") // fix hardcoded stuff later after MVP.
    .attr("width", "10%")
    .attr("height", "35%")
clefs.enter()
    .append("svg:image")
    .attr("xlink:href", "http://www.tntmusicbox.com/content/Freebies/free%20images%20for%20download/png/Bass%20Clef.png")
    .attr("x", "10")
    .attr("y", "65%")
    .attr("width", "10%")
    .attr("height", "25%")

/* ---------------- Parse the MIDI file ---------------- */

