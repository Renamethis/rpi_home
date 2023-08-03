import { useEffect, useMemo, useState } from "react";
import { useNavigate } from 'react-router-dom';
import * as d3 from "d3";
import { useSpring, animated } from "@react-spring/web";
import { colours } from "./Colorus.js"

export const MARGIN = { top: 30, right: 30, bottom: 50, left: 50 };

type EnvironmentPoint = { x : number; temperature : number; pressure: number; 
                          humidity : number; illumination : number; 
                          dust : number; oxidising: number; reducing : number; 
                          nh3 : number, datetime: string};

type LineChartProps = {
  width: number;
  height: number;
  data: EnvironmentPoint[];
  selectedGroup: "temperature" | "pressure" | "humidity" | "illumination" | "dust" | "oxidising" | "reducing" | "nh3";
};

export const LineChart = ({
  axesRef,
  entries,
  width,
  height,
  data,
  selectedGroup,
}: LineChartProps) => {
    const navigate = useNavigate();
    const boundsWidth = width - MARGIN.right - MARGIN.left;
    const boundsHeight = height - MARGIN.top - MARGIN.bottom;
    const values = Object.entries(data).map(([_, v]) => v[selectedGroup])
    const max = d3.max(values);
    const min = d3.min(values);
    const yScale = useMemo(() => {
        return d3.scaleLinear().domain([Math.round(min * 0.9), Math.round(max * 1.1)]).range([boundsHeight, 0]);
    }, [data, height, max, min]);

    const xScale = useMemo(() => {
        return d3.scaleLinear().domain([-1, entries]).range([0, boundsWidth]);
    }, [data, width]);

  // Render the X and Y axis using d3.js, not react
  useEffect(() => {
    const svgElement = d3.select(axesRef.current);
    const Tooltip = svgElement.append("div")
    .style("opacity", 0)
    .attr("class", "tooltip")
    .style("background-color", "white")
    .style("border", "solid")
    .style("border-width", "2px")
    .style("border-radius", "5px")
    .style("padding", "5px")

    svgElement.selectAll("g").remove();
    svgElement.selectAll("g").remove();
    const xAxisGenerator = d3.axisBottom(xScale);
    svgElement
      .append("g")
      .attr("class", "x axis")
      .attr("transform", "translate(0," + boundsHeight + ")")
      .transition()
      .duration(750)
      .call(xAxisGenerator);

    const yAxisGenerator = d3.axisLeft(yScale);
    svgElement.append("g")
              .attr("class", "y axis")
              .transition()
              .duration(750)
              .call(yAxisGenerator);

    svgElement.selectAll('circle')
              .data(data)
              .join("circle")
              .transition()
              .duration(630)
              .attr("class", "circle")
              .attr("cx", d => xScale(d.x))
              .attr("cy", d => yScale(d[String(selectedGroup)]))
              .attr("r", 5)
              .attr("stroke", "#69b3a2")
              .attr("stroke-width", 3)
              .attr("fill", "white")
      svgElement.selectAll('circle')
              .on("click", function(event, a) {
                const time = event.target.__data__.datetime
                navigate('weather', {state:{date:time}})
              });
        

      svgElement.selectAll('circle')
      
  }, [xScale, yScale, boundsHeight]);

  const lineBuilder = d3
    .line<EnvironmentPoint>()
    .x((d) => xScale(d.x))
    .y((d) => yScale(d[selectedGroup]));
  const linePath = lineBuilder(data);
  if (!linePath) {
    return null;
  }
  return (
     <div>
      <svg width={width} height={height}>
        {/* first group is lines */}
        <g
          width={boundsWidth}
          height={boundsHeight}
          transform={`translate(${[MARGIN.left, MARGIN.top].join(",")})`}
        >
          <LineItem
            path={linePath}
            color={colours[selectedGroup]}
          />
        </g>
        {/* Second is for the axes */}
        <g
          width={boundsWidth}
          height={boundsHeight}
          ref={axesRef}
          transform={`translate(${[MARGIN.left, MARGIN.top].join(",")})`}
        />
      </svg>
    </div>
  );
};

type LineItemProps = {
  path: string;
  color: string;
};

const LineItem = ({ path, color }: LineItemProps) => {
  const springProps = useSpring({
    to: {
      path,
      color,
    },
    config: {
      friction: 40,
    },
  });

  return (
    <animated.path
      d={springProps.path}
      fill={"none"}
      stroke={color}
      strokeWidth={2}
    />
  );
};

