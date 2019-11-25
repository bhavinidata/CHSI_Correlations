const svgWidth = 560;
const svgHeight = 320;

const margin = {
    top: 20,
    right: 40,
    bottom: 80,
    left: 100
};

// Calculate chart width and height
const width = svgWidth - margin.left - margin.right;
const height = svgHeight - margin.top - margin.bottom;

// Create an SVG wrapper, append an SVG group that will hold our chart,
// and shift the latter by left and top margins.
const svg = d3.select("#scatter-state")
            .append("svg")
            .attr("width", svgWidth)
            .attr("height", svgHeight);

// Append SVG group
const chartGroup = svg.append("g")
.attr("transform", `translate(${margin.left}, ${margin.top})`)

// Initial params
var chosenXaxis = "poverty";
var chosenYaxis = "obesity";

// function used for updating xAxis const upon click on axis label
function renderXAxes(newXScale, xAxis) {
  const bottomAxis = d3.axisBottom(newXScale);

  xAxis.transition()
    .duration(1000)
    .call(bottomAxis);

  return xAxis;
}
// function used for updating yAxis const upon click on axis label
function renderYAxes(newYScale, yAxis) {
  const leftAxis = d3.axisLeft(newYScale);

  yAxis.transition()
    .duration(1000)
    .call(leftAxis);

  return yAxis;
}


// function used for updating circles group with a transition to
// new circles
function renderCircles(circlesGroup, newXScale, newYScale, chosenXAxis, chosenYAxis) {
  circlesGroup.transition()
    .duration(1000)
    .attr("cx", d => newXScale(d[chosenXAxis]))
    .attr("cy", d=>newYScale(d[chosenYAxis]));
  return circlesGroup;
}
function renderTexts(txtGroup, newXScale, newYScale, chosenXAxis, chosenYAxis) {
  txtGroup.transition()
    .duration(1000)
    .attr("x", d=>newXScale(d[chosenXAxis]))
    .attr("y", d=>newYScale(d[chosenYAxis]))
  return txtGroup;
}

// function used for updating x-scale const upon click on axis label
function xScale(healthData, chosenXaxis) {
    // create scales
    const xLinearScale = d3.scaleLinear()
      .domain([d3.min(healthData, d => d[chosenXaxis]*0.8),
        d3.max(healthData, d => d[chosenXaxis]*1.2)
      ])
      .range([0, width]);
    return xLinearScale;
}
function yScale(healthData, chosenYaxis) {
    // create scales
    const yLinearScale = d3.scaleLinear()
      .domain([d3.min(healthData, d=>d[chosenYaxis])*0.8, d3.max(healthData, d=>d[chosenYaxis])*1.2 ])
      .range([height, 0]);
    return yLinearScale;
}

// function used for updating tooltip for circles group
function updateToolTip(chosenXaxis, chosenYaxis, circlesGroup, state_county){
    console.log("in update tooltip")
    let xLabel = ""
    let yLabel = ""
    if (chosenXaxis === "poverty"){
      xLabel = "Poverty: ";
    }
    else if (chosenXaxis === "few_fruit_veg"){
      xLabel = "Few Fruit_Veg: ";
    }
    else{
      xLabel = "Primary Care Physician Rate: ";
    }
    if (chosenYaxis === "obesity"){
      yLabel = "Obesity: "
    }
    else if (chosenYaxis === "diabetes"){
      yLabel = "Diabetes: "
    }
    else{
      yLabel = "High Blood Pressure: "
    }
    const toolTip = d3.tip()
                      .attr("class", "d3-tip")
                      .offset([80, -60])
                      .html(function(d){
                        if(state_county == 0){
                            console.log(d.chsi_state_name)
                            return(`${d.chsi_state_name},${d.chsi_state_abbr}<br>${xLabel}${d[chosenXaxis]}%<br>${yLabel}${d[chosenYaxis]}%`)
                        }
                        else{
                            return(`${d.chsi_county_name}<br>${xLabel}${d[chosenXaxis]}%<br>${yLabel}${d[chosenYaxis]}%`)
                        }
                      })
    
    circlesGroup.call(toolTip);
    circlesGroup.on("mouseover", function(data){
      toolTip.show(data, this);
      d3.select(this).style("stroke", "black");
      
    })
    circlesGroup.on("mouseout", function(data, index){
      toolTip.hide(data, this)
      d3.select(this).style("stroke", "white");
    })
    return circlesGroup;
  }
  

// Retrieve data from the CSV file and execute everything below
(async function(){
    console.log("in func")
    const defaultURL = `/demog_riskfact_statewise` 
    let healthData = await d3.json(defaultURL);
        console.log(healthData);
    
     // parse data to interger from string
     healthData.forEach(function(data){
        console.log(data.poverty)
        data.poverty = +data.poverty;
        data.few_fruit_veg = +data.few_fruit_veg;
        data.diabetes = +data.diabetes;
        data.obesity = +data.obesity;
        console.log(data.obesity)
        data.high_blood_pres = +data.high_blood_pres;
        data.prim_care_phys_rate = +data.prim_care_phys_rate;
    })
    console.log(healthData)
    // xLinearScale function after csv import
    let xLinearScale = xScale(healthData, chosenXaxis);

    // yLinearScale function after csv import
    let yLinearScale = yScale(healthData, chosenYaxis)

    // Create initial axis functions
    const bottomAxis = d3.axisBottom(xLinearScale);
    const leftAxis = d3.axisLeft(yLinearScale);

    // append X-axis
    let xAxis = chartGroup.append("g")
                        .classed("x-axis", true)
                        .attr("transform", `translate(0, ${height})`)
                        .call(bottomAxis)
    
    let yAxis = chartGroup.append("g")
                        .classed("y-axis", true)
                        .call(leftAxis)
    
    let crlTxtGroup = chartGroup.selectAll("mycircles")
                      .data(healthData)
                      .enter()
                      .append("g")
    
    let circlesGroup = crlTxtGroup.append("circle")
                            .attr("cx", d=>xLinearScale(d[chosenXaxis]))
                            .attr("cy", d=>yLinearScale(d[chosenYaxis]))
                            .classed("stateCircle", true)
                            .attr("r", 8)
                            .attr("opacity", "1");

    let txtGroup = crlTxtGroup.append("text")
                              .text(d=>d.chsi_state_abbr)
                              .attr("x", d=>xLinearScale(d[chosenXaxis]))
                              .attr("y", d=>yLinearScale(d[chosenYaxis])+3)
                              .classed("stateText", true)
                              .style("font-size", "7px")
                              .style("font-weight", "800")

     // Create group for  3 x- axis labels
     const xlabelsGroup = chartGroup.append("g")
                                .attr("transform", `translate(${width / 2}, ${height + 20 + margin.top})`);
    
    // Create group for  3 y- axis labels
    const ylabelsGroup = chartGroup.append("g")
                                .attr("transform", `translate(${0-margin.left/4}, ${height/2})`);

    const povertyLabel = xlabelsGroup.append("text")
                                .attr("x", 0)
                                .attr("y", 0)
                                .attr("value", "poverty") // value to grab for event listener
                                .classed("active", true)
                                .classed("aText", true)
                                .text("Poverty (%)");

    const few_fruit_veg_Label = xlabelsGroup.append("text")
                                .attr("x", 0)
                                .attr("y", 20)
                                .attr("value", "few_fruit_veg") // value to grab for event listener
                                .classed("inactive", true)
                                .classed("aText", true)
                                .text("Few Fruits and Veg(%)");
    
    const prim_care_phys_rateLabel = xlabelsGroup.append("text")
                                .attr("x", 0)
                                .attr("y", 40)
                                .attr("value", "prim_care_phys_rate") // value to grab for event listener
                                .classed("inactive", true)
                                .classed("aText", true)
                                .text("Primary Care Physicians available (%)");

    const obesityLabel = ylabelsGroup.append("text")
                                .attr("y", 0 - 20)
                                .attr("x", 0)
                                .attr("transform", "rotate(-90)")
                                .attr("dy", "1em")
                                .attr("value", "obesity")
                                .classed("active", true)
                                .classed("aText", true)
                                .text("Obesity (%)");

    const diabetesLabel = ylabelsGroup.append("text")
                                .attr("y", 0 - 40)
                                .attr("x", 0)
                                .attr("transform", "rotate(-90)")
                                .attr("dy", "1em")
                                .attr("value", "diabetes")
                                .classed("inactive", true)
                                .classed("aText", true)
                                .text("Diabetes (%)");

    const highbplabel = ylabelsGroup.append("text")
                                .attr("y", 0 - 60)
                                .attr("x", 0)
                                .attr("transform", "rotate(-90)")
                                .attr("dy", "1em")
                                .attr("value", "high_blood_pres")
                                .classed("inactive", true)
                                .classed("aText", true)
                                .text("High Blood Pressure (%)");
    
    // update tooltip with new info after changing x-axis 
    circlesGroup = updateToolTip(chosenXaxis, chosenYaxis, circlesGroup, county=0); 

    // x axis labels event listener
    xlabelsGroup.selectAll("text")
        .on("click", function() {
        // get value of selection
        const value = d3.select(this).attr("value");
        console.log(`${value} click`)
        if (value !== chosenXaxis) {

            // replaces chosenXAxis with value
            chosenXaxis = value;
            console.log(chosenXaxis)

            // functions here found above csv import
            // updates x scale for new data
            xLinearScale = xScale(healthData, chosenXaxis);

            // updates x axis with transition
            xAxis = renderXAxes(xLinearScale, xAxis);

            // updates circles with new x values
            circlesGroup = renderCircles(circlesGroup, xLinearScale, yLinearScale, chosenXaxis, chosenYaxis);

             // updates texts with new x values
            txtGroup = renderTexts(txtGroup, xLinearScale, yLinearScale, chosenXaxis, chosenYaxis);

            // changes classes to change bold text
            if (chosenXaxis === "poverty") {
                povertyLabel
                    .classed("active", true)
                    .classed("inactive", false);
                few_fruit_veg_Label
                    .classed("active", false)
                    .classed("inactive", true);
                prim_care_phys_rateLabel
                    .classed("active", false)
                    .classed("inactive", true);
            }
            else if (chosenXaxis === "few_fruit_veg"){
                povertyLabel
                    .classed("active", false)
                    .classed("inactive", true);
                few_fruit_veg_Label
                    .classed("active", true)
                    .classed("inactive", false);
                prim_care_phys_rateLabel
                    .classed("active", false)
                    .classed("inactive", true);
            }
            else{
                povertyLabel
                    .classed("active", false)
                    .classed("inactive", true);
                few_fruit_veg_Label
                    .classed("active", false)
                    .classed("inactive", true);
                prim_care_phys_rateLabel
                    .classed("active", true)
                    .classed("inactive", false);  
            }
          // update tooltip with new info after changing x-axis 
          circlesGroup = updateToolTip(chosenXaxis, chosenYaxis, circlesGroup, county=0); 
      }})
// y axis labels event listener
ylabelsGroup.selectAll("text")
.on("click", function() {
// get value of selection
const value = d3.select(this).attr("value");
console.log(`${value} click`)
if (value !== chosenYaxis) {

    // replaces chosenXAxis with value
    chosenYaxis = value;
    console.log(chosenYaxis)

    // functions here found above csv import
    // updates x scale for new data
    yLinearScale = yScale(healthData, chosenYaxis);

    // updates x axis with transition
    yAxis = renderYAxes(yLinearScale, yAxis);

    // updates circles with new x values
    circlesGroup = renderCircles(circlesGroup, xLinearScale, yLinearScale, chosenXaxis, chosenYaxis);

     // updates texts with new x values
    txtGroup = renderTexts(txtGroup, xLinearScale, yLinearScale, chosenXaxis, chosenYaxis);

    // changes classes to change bold text
    if (chosenYaxis === "obesity") {
        obesityLabel
            .classed("active", true)
            .classed("inactive", false);
        diabetesLabel
            .classed("active", false)
            .classed("inactive", true);
        highbplabel
            .classed("active", false)
            .classed("inactive", true);
    }
    else if (chosenYaxis === "diabetes"){
        obesityLabel
            .classed("active", false)
            .classed("inactive", true);
        diabetesLabel
            .classed("active", true)
            .classed("inactive", false);
        highbplabel
            .classed("active", false)
            .classed("inactive", true);
    }
    else{
        obesityLabel
            .classed("active", false)
            .classed("inactive", true);
        diabetesLabel
            .classed("active", false)
            .classed("inactive", true);
        highbplabel
            .classed("active", true)
            .classed("inactive", false);  
    }
     // update tooltip with new info after changing y-axis 
     circlesGroup = updateToolTip(chosenXaxis, chosenYaxis, circlesGroup, county=0); 
  }})

  circlesGroup.on("click", function(data){
      if (!(d3.select(".svg-county").empty())){
          console.log("svg not empty")
        d3.select(".svg-county").remove()
        // d3.select(".county_graph").select(h3).remove()
        }
        console.log("Circle clicked!")
        console.log(chosenXaxis)
        console.log(data.chsi_state_name)
        // Create an SVG wrapper, append an SVG group that will hold our chart,
        // and shift the latter by left and top margins.
        
        const svg = d3.select("#scatter-county")
                    .append("svg")
                    .classed("svg-county", true)
                    .attr("width", svgWidth)
                    .attr("height", svgHeight);
        // d3.select(".county_graph").append(h3).text("county analysis")
        // Append SVG group
        const chartGroupCounty = svg.append("g")
            .attr("transform", `translate(${margin.left}, ${margin.top})`)
        countyData(data)

        async function countyData(data){
            console.log("in pop func")
            let state_name = data.chsi_state_name;
            const defaultcountyURL = `/demo_riskfactor_countywise/${state_name}` 
            let countyhealthData = await d3.json(defaultcountyURL);
            console.log(countyhealthData);

            // parse data to interger from string
            countyhealthData.forEach(function(data){
                console.log(data.poverty)
                data.poverty = +data.poverty;
                data.few_fruit_veg = +data.few_fruit_veg;
                data.diabetes = +data.diabetes;
                data.obesity = +data.obesity;
                console.log(data.obesity)
                data.high_blood_pres = +data.high_blood_pres;
                data.prim_care_phys_rate = +data.prim_care_phys_rate;
            })
            console.log(countyhealthData)
            // xLinearScale function after csv import
            let xLinearScale = xScale(countyhealthData, chosenXaxis);

            // yLinearScale function after csv import
            let yLinearScale = yScale(countyhealthData, chosenYaxis)

            // Create initial axis functions
            const bottomAxis = d3.axisBottom(xLinearScale);
            const leftAxis = d3.axisLeft(yLinearScale);

            // append X-axis
            let xAxis = chartGroupCounty.append("g")
                                .classed("x-axis-county", true)
                                .attr("transform", `translate(0, ${height})`)
                                .call(bottomAxis)

            let yAxis = chartGroupCounty.append("g")
                                .classed("y-axis-county", true)
                                .call(leftAxis)

            let crlTxtGroup = chartGroupCounty.selectAll("countycircles")
                                .data(countyhealthData)
                                .enter()
                                .append("g")

            let countycirclesGroup = crlTxtGroup.append("circle")
                                    .attr("cx", d=>xLinearScale(d[chosenXaxis]))
                                    .attr("cy", d=>yLinearScale(d[chosenYaxis]))
                                    .classed("countyCircle", true)
                                    .attr("r", 8)
                                    .attr("opacity", "1");

                // Create group for  3 x- axis labels
            const xlabelsGroup = chartGroupCounty.append("g")
                .attr("transform", `translate(${width / 2}, ${height + 20 + margin.top})`);

            // Create group for  3 y- axis labels
            const ylabelsGroup = chartGroupCounty.append("g")
                .attr("transform", `translate(${0-margin.left/4}, ${height/2})`);

            const xLabel = xlabelsGroup.append("text")
                .attr("transform", `translate(${width / 2}, ${height + 20 + margin.top})`)
                // .attr("x", 0)
                // .attr("y", 0)
                .attr("value", chosenXaxis) // value to grab for event listener
                .classed("active", true)
                .classed("aText", true)
                .text(chosenXaxis);

            const yLabel = ylabelsGroup.append("text")
                .attr("transform", `translate(${0-margin.left/4}, ${(height/20)})`)
                .attr("y", 0 - 20)
                .attr("x", 0)
                .attr("transform", "rotate(-90)")
                // .attr("dy", "1em")
                .attr("value", chosenYaxis)
                .classed("active", true)
                .classed("aText", true)
                .text(chosenYaxis)
            countycirclesGroup = updateToolTip(chosenXaxis, chosenYaxis, countycirclesGroup, county=1); 
            }
        })

})()